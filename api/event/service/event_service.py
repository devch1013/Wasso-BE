from datetime import datetime, timedelta

from django.utils import timezone
from rest_framework.exceptions import PermissionDenied

from api.club.models import Generation, GenMember
from api.club.models.club_apply import ClubApply
from api.event.models import Attendance, AttendanceStatus, Event
from api.event.models.abusing import Abusing
from api.event.serializers import (
    CheckQRCodeSerializer,
    EventCreateSerializer,
    EventUpdateSerializer,
)
from api.userapp.models import User
from api.userapp.models.user_meta import Platform, UniqueToken
from common.component import FCMComponent, NotificationTemplate, UserSelector
from common.exceptions import CustomException, ErrorCode
from common.utils.code_generator import HashTimeGenerator
from common.utils.qr_code import generate_uuid_qr_for_imagefield

fcm_component = FCMComponent()


class EventService:
    @staticmethod
    def create_event(data: EventCreateSerializer, user):
        print("data", data)
        generation_id = data.validated_data.get("generation_id")
        # 사용자가 클럽의 관리자인지 확인
        try:
            if not GenMember.objects.get(
                member__user=user, generation__id=generation_id
            ).is_admin():
                raise PermissionDenied("클럽 관리자만 이벤트를 생성할 수 있습니다.")
        except GenMember.DoesNotExist:
            raise PermissionDenied("클럽 관리자만 이벤트를 생성할 수 있습니다.")
        generation = Generation.objects.get(id=generation_id)
        qr_code, qr_file = generate_uuid_qr_for_imagefield()

        event = Event.objects.create(
            generation=generation,
            title=data.validated_data.get("title"),
            description=data.validated_data.get("description"),
            location=data.validated_data.get("location"),
            location_link=data.validated_data.get("location_link"),
            images=data.validated_data.get("images"),
            date=data.validated_data.get("date"),
            start_datetime=data.validated_data.get("start_time"),
            end_datetime=data.validated_data.get("end_time"),
            start_minutes=data.validated_data.get("start_minutes"),
            late_minutes=data.validated_data.get("late_minutes"),
            fail_minutes=data.validated_data.get("fail_minutes"),
            qr_code=qr_code,
            qr_code_url=qr_file,
        )

        users = UserSelector.get_users_by_generation(generation)
        fcm_component.send_to_users(
            users,
            NotificationTemplate.EVENT_CREATE.get_title(),
            NotificationTemplate.EVENT_CREATE.get_body(club_name=generation.club.name),
            data=NotificationTemplate.EVENT_CREATE.get_deeplink_data(event_id=event.id),
        )

    @staticmethod
    def update_event(data: EventUpdateSerializer, user, event_id):
        # TODO: user가 이벤트 관리자인지 확인
        event = Event.objects.get(id=event_id)
        if data.validated_data.get("title") is not None:
            event.title = data.validated_data.get("title")
        if data.validated_data.get("description") is not None:
            event.description = data.validated_data.get("description")
        if data.validated_data.get("location") is not None:
            event.location = data.validated_data.get("location")

        additional_images = data.validated_data.get("additional_images")
        deleted_images = data.validated_data.get("deleted_images")
        print("additional_images", additional_images)
        print("deleted_images", deleted_images)
        event.update_images(additional_images, deleted_images)

        if data.validated_data.get("location_link") is not None:
            event.location_link = data.validated_data.get("location_link")

        if data.validated_data.get("start_time") is not None:
            event.start_datetime = data.validated_data.get("start_time")
        if data.validated_data.get("end_time") is not None:
            event.end_datetime = data.validated_data.get("end_time")
        if data.validated_data.get("date") is not None:
            event.date = data.validated_data.get("date")
        if data.validated_data.get("start_minutes") is not None:
            event.start_minutes = data.validated_data.get("start_minutes")
        if data.validated_data.get("late_minutes") is not None:
            event.late_minutes = data.validated_data.get("late_minutes")
        if data.validated_data.get("fail_minutes") is not None:
            event.fail_minutes = data.validated_data.get("fail_minutes")

        event.save()

    @staticmethod
    def check_qr_code(serializer: CheckQRCodeSerializer, event: Event, user: User):
        # TODO: 캐싱하기
        valid_code = HashTimeGenerator.auto_generate_code_list(event.qr_code)
        if serializer.validated_data.get("qr_code") not in valid_code:
            raise CustomException(ErrorCode.INVALID_QR_CODE)

        try:
            generation_mapping = GenMember.objects.get(
                member__user=user, generation=event.generation
            )
        except GenMember.DoesNotExist:
            if ClubApply.objects.filter(
                user=user, generation=event.generation, accepted=False
            ).exists():
                raise CustomException(ErrorCode.WAITING_FOR_APPROVAL)
            else:
                raise CustomException(ErrorCode.NOT_REGISTERED_CLUB)

        if (
            attendance := Attendance.objects.filter(
                event=event, generation_mapping=generation_mapping
            )
            .order_by("-created_at")
            .first()
        ):
            if attendance.status != AttendanceStatus.UNCHECKED:
                raise CustomException(ErrorCode.ALREADY_CHECKED_IN)

        unique_token = None

        if serializer.validated_data.get("device_id", None):
            unique_token = UniqueToken.objects.filter(
                token=serializer.validated_data.get("device_id")
            ).first()
            if not unique_token:
                unique_token = UniqueToken.objects.create(
                    user=user,
                    token=serializer.validated_data.get("device_id"),
                    platform=Platform.UNKNOWN,
                    model=serializer.validated_data.get("model", None),
                )

        print(serializer.validated_data)
        # 계속 생성되게 변경
        attendance = Attendance.objects.create(
            event=event,
            generation_mapping=generation_mapping,
            status=EventService.check_attendance_status(event),
            latitude=serializer.validated_data.get("latitude", None),
            longitude=serializer.validated_data.get("longitude", None),
            is_modified=False,
            unique_token=unique_token,
        )

        if unique_token:
            duplicated_attendance = (
                event.attendances.filter(unique_token=unique_token)
                .exclude(id=attendance.id)
                .first()
            )
            if duplicated_attendance:
                Abusing.objects.create(
                    attendance=duplicated_attendance,
                    reason=f"중복 출석 - {duplicated_attendance.generation_mapping.member.user.username}",
                )

        # if serializer.validated_data.get("device_id", None):
        #     if event.attendances.

        #     Abusing.objects.create(
        #         attendance=attendance,
        #         reason=serializer.validated_data.get("reason", None),
        #     )

        return attendance

    @staticmethod
    def check_attendance_status(event: Event):
        start_date_time = timezone.make_aware(
            datetime.combine(event.date, event.start_time)
        )

        late_time = start_date_time + timedelta(minutes=event.late_minutes)
        early_time = start_date_time + timedelta(minutes=event.start_minutes)
        fail_time = start_date_time + timedelta(minutes=event.fail_minutes)
        current_time = timezone.localtime(timezone.now())
        if current_time < late_time and current_time >= early_time:
            return AttendanceStatus.PRESENT
        elif current_time >= late_time and current_time < fail_time:
            return AttendanceStatus.LATE
        elif current_time >= fail_time:
            return AttendanceStatus.ABSENT
        else:
            raise CustomException(ErrorCode.INVALID_TIME)

    @staticmethod
    def change_attendance_status(
        event_id: int,
        member_id: int,
        status: int,
        user: User,
        send_notification: bool = True,
    ):
        # 가장 최근의 attendance 레코드를 가져옴
        attendance = (
            Attendance.objects.filter(
                event__id=event_id, generation_mapping__member__id=member_id
            )
            .order_by("-created_at")
            .first()
        )

        # attendance가 없는 경우, 새로 생성
        if attendance is None or attendance.status != status:
            event = Event.objects.get(id=event_id)
            generation_mapping = GenMember.objects.get(
                member__id=member_id, generation=event.generation
            )
            modify_user = GenMember.objects.get(
                member__user=user, generation=event.generation
            )
            attendance = Attendance.objects.create(
                event=event,
                generation_mapping=generation_mapping,
                status=status,
                created_by=modify_user,
                is_modified=True,
            )
            # 새로 생성된 경우에는 알림을 보냄
            if send_notification:
                fcm_component.send_to_user(
                    attendance.generation_mapping.member.user,
                    NotificationTemplate.ATTENDANCE_CHANGE.get_title(),
                    NotificationTemplate.ATTENDANCE_CHANGE.get_body(
                        event_name=attendance.event.title,
                        attendance_status=AttendanceStatus(status).label,
                    ),
                    data=NotificationTemplate.ATTENDANCE_CHANGE.get_deeplink_data(
                        event_id=event.id,
                    ),
                )

        return attendance

    @staticmethod
    def attend_all(event: Event, user: User):
        generation_mappings = GenMember.objects.filter(generation=event.generation)
        for generation_mapping in generation_mappings:
            # TODO: 알림 한번에 보내기
            EventService.change_attendance_status(
                event.id, generation_mapping.member.id, AttendanceStatus.PRESENT, user
            )

    @staticmethod
    def get_me(event: Event, user: User):
        generation_mapping = GenMember.objects.get(
            member__user=user, generation=event.generation
        )
        try:
            attendance = (
                Attendance.objects.filter(
                    event=event, generation_mapping=generation_mapping
                )
                .order_by("-created_at")
                .first()
            )
            if attendance is None or attendance.status is None:
                return Attendance(status=AttendanceStatus.UNCHECKED)
            return attendance
        except Attendance.DoesNotExist:
            return Attendance(status=AttendanceStatus.UNCHECKED)

    @staticmethod
    def get_member_log(event: Event, gen_member_id: int):
        generation_mapping = GenMember.objects.get(id=gen_member_id)

        # is_modified가 True인 것 중 가장 최근 생성된 것
        latest_modified = (
            Attendance.objects.filter(
                event=event, generation_mapping=generation_mapping, is_modified=True
            )
            .order_by("-created_at")
            .first()
        )

        # is_modified가 False인 것 중 가장 최근 생성된 것
        latest_unmodified = (
            Attendance.objects.filter(
                event=event, generation_mapping=generation_mapping, is_modified=False
            )
            .order_by("-created_at")
            .first()
        )

        return {"modified": latest_modified, "unmodified": latest_unmodified}

    @staticmethod
    def get_generation_info(event_id: int):
        event = Event.objects.get(id=event_id)
        return event.generation

    @classmethod
    def get_recent_event(cls, generation_id: int):
        generation = Generation.objects.get(id=generation_id)
        event = (
            Event.objects.filter(generation=generation)
            .order_by("-start_datetime")
            .first()
        )
        if event is None:
            return None
        return event
