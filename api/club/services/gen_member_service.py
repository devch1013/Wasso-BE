from api.club.models import GenMember, Role
from api.event.models import Attendance, Event
from api.event.models.enums import AttendanceStatus
from api.event.serializers import AttendanceSerializer
from common.component import FCMComponent, NotificationTemplate
from common.exceptions import CustomException, ErrorCode

fcm_component = FCMComponent()


class GenMemberService:
    @staticmethod
    def update_gen_member(gen_member: GenMember, role_id: int):
        role = Role.objects.get(id=role_id)
        if gen_member.generation.club != role.club:
            raise CustomException(ErrorCode.ROLE_NOT_FOUND)
        if gen_member.role.is_superuser() and not gen_member.role == role:
            all_gen_members = GenMember.objects.filter(generation=gen_member.generation)
            superuser_count = 0
            for m in all_gen_members:
                if m.role.is_superuser():
                    superuser_count += 1
            if superuser_count <= 1:
                raise CustomException(ErrorCode.OWNER_ROLE_MUST_BE_MORE_THAN_ONE)
        gen_member.role = role
        gen_member.save()
        fcm_component.send_to_user(
            gen_member.member.user,
            NotificationTemplate.MEMBER_ROLE_CHANGE.get_title(),
            NotificationTemplate.MEMBER_ROLE_CHANGE.get_body(
                club_name=gen_member.generation.club.name, role_name=role.name
            ),
            data=NotificationTemplate.MEMBER_ROLE_CHANGE.get_deeplink_data(),
        )

    @staticmethod
    def delete_gen_member(gen_member: GenMember):
        if gen_member.role.is_superuser():
            raise CustomException(ErrorCode.OWNER_CANNOT_BE_DELETED)
        gen_member.delete()

    @classmethod
    def get_gen_member_attendances(cls, gen_member_id: int):
        gen_member = GenMember.objects.get(id=gen_member_id)

        # 해당 GenMember의 generation에 속한 모든 Event 가져오기
        events = Event.objects.filter(generation=gen_member.generation).order_by(
            "-date", "-start_datetime"
        )

        # 모든 Event에 대한 해당 GenMember의 Attendance를 한 번에 가져오기
        attendances = Attendance.objects.filter(
            event__in=events, generation_mapping=gen_member
        ).order_by("event_id", "-created_at")

        # 각 Event에 대한 최신 Attendance만 필터링 (event_id별로 가장 최신 것만)
        latest_attendances_map = {}
        for attendance in attendances:
            if attendance.event_id not in latest_attendances_map:
                latest_attendances_map[attendance.event_id] = attendance

        # 출석 통계 계산
        total_attendances = 0
        total_absences = 0
        total_late_attendances = 0

        for attendance in latest_attendances_map.values():
            if attendance.status == AttendanceStatus.PRESENT:
                total_attendances += 1
            elif attendance.status == AttendanceStatus.LATE:
                total_late_attendances += 1
            elif attendance.status == AttendanceStatus.ABSENT:
                total_absences += 1

        # EventSerializer 구조에 맞춘 이벤트 데이터 구성
        events_data = []
        for event in events:
            event_data = {
                "id": event.id,
                "title": event.title,
                "date": event.date,
                "start_time": event.start_time,
                "attendance": None,
            }

            # 해당 Event의 최신 Attendance가 있다면 직렬화
            latest_attendance = latest_attendances_map.get(event.id)
            if latest_attendance:
                print("latest_attendance", latest_attendance)
                event_data["attendance"] = AttendanceSerializer(latest_attendance).data
                print("event_data", event_data["attendance"])

            events_data.append(event_data)

        # GenMemberAttendanceSerializer 구조에 맞춘 최종 데이터 구성
        result_data = {
            "username": gen_member.member.user.username,
            "email": gen_member.member.user.email,
            "attendance_stats": {
                "total_attendances": total_attendances,
                "total_absences": total_absences,
                "total_late_attendances": total_late_attendances,
            },
            "events": events_data,
        }

        print("result_data", result_data)

        # Serializer를 사용해서 최종 결과 반환
        # serializer = GenMemberAttendanceSerializer(data=result_data)
        # serializer.is_valid(raise_exception=True)
        # print("serializer.validated_data", serializer.validated_data)
        # return serializer.validated_data
        return result_data
