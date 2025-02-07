from datetime import datetime, timedelta

from django.utils import timezone
from rest_framework.exceptions import PermissionDenied

from club.models import Generation, GenerationMapping
from main.exceptions import CustomException, ErrorCode
from userapp.models import User
from utils.qr_code import generate_uuid_qr_for_imagefield

from ..models import Attendance, AttendanceStatus, Event
from ..serializers import CheckQRCodeSerializer, EventCreateSerializer


class EventService:
    @staticmethod
    def create_event(data: EventCreateSerializer, user):
        generation_id = data.validated_data.get("generation_id")
        # 사용자가 클럽의 관리자인지 확인
        try:
            if not GenerationMapping.objects.get(
                member__user=user, generation__id=generation_id
            ).is_admin():
                raise PermissionDenied("클럽 관리자만 이벤트를 생성할 수 있습니다.")
        except GenerationMapping.DoesNotExist:
            raise PermissionDenied("클럽 관리자만 이벤트를 생성할 수 있습니다.")
        generation = Generation.objects.get(id=generation_id)
        qr_code, qr_file = generate_uuid_qr_for_imagefield()

        Event.objects.create(
            generation=generation,
            title=data.validated_data.get("title"),
            description=data.validated_data.get("description"),
            location=data.validated_data.get("location"),
            images=data.validated_data.get("images"),
            date=data.validated_data.get("date"),
            start_time=data.validated_data.get("start_time"),
            end_time=data.validated_data.get("end_time"),
            start_minutes=data.validated_data.get("start_minute"),
            late_minutes=data.validated_data.get("late_minute"),
            fail_minutes=data.validated_data.get("fail_minute"),
            qr_code=qr_code,
            qr_code_url=qr_file,
        )

    @staticmethod
    def check_qr_code(serializer: CheckQRCodeSerializer, event: Event, user: User):
        if serializer.validated_data.get("qr_code") != event.qr_code:
            raise CustomException(ErrorCode.INVALID_QR_CODE)
        generation_mapping = GenerationMapping.objects.get(
            member__user=user, generation=event.generation
        )
        try:
            Attendance.objects.get(event=event, generation_mapping=generation_mapping)
            raise CustomException(ErrorCode.ALREADY_CHECKED)
        except Attendance.DoesNotExist:
            status = EventService.check_attendance_status(event)
            print(status)
            attendance = Attendance.objects.create(
                event=event,
                generation_mapping=generation_mapping,
                status=status,
                latitude=serializer.validated_data.get("latitude"),
                longitude=serializer.validated_data.get("longitude"),
            )
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
    def change_attendance_status(event_id: int, member_id: int, status: int):
        try:
            attendance = Attendance.objects.get(
                event__id=event_id, generation_mapping__member__id=member_id
            )
        except Attendance.DoesNotExist:
            event = Event.objects.get(id=event_id)
            generation_mapping = GenerationMapping.objects.get(
                member__id=member_id, generation=event.generation
            )
            attendance = Attendance.objects.create(
                event=event, generation_mapping=generation_mapping, status=status
            )
        attendance.modify_attendance(status)
        return attendance
