import logging
from datetime import datetime, timedelta

from celery import shared_task
from django.utils import timezone

from api.club.models.generation_mapping import GenMember
from api.event.models import Attendance, Event
from api.event.models.enums import AttendanceStatus

logger = logging.getLogger(__name__)


@shared_task
def mark_absent_for_past_events():
    """
    이벤트 시작 시간에 fail_minutes를 더한 시간이 지난 이벤트에 대해
    출석 전인 상태의 멤버와 출석 상태가 없는 멤버들을 결석으로 처리합니다.
    """
    logger.info("Starting mark_absent_for_past_events job")

    now = timezone.localtime(timezone.now())
    today = now.date()

    # 오늘 날짜의 이벤트 중 fail_minutes가 지난 이벤트 찾기
    events = Event.objects.filter(date=today)

    processed_events = 0
    total_updated = 0
    total_created = 0

    for event in events:
        # 이벤트 시작 시간에 fail_minutes를 더한 시간 계산
        event_datetime = datetime.combine(event.date, event.start_time)
        event_datetime = timezone.make_aware(event_datetime)
        absent_time = event_datetime + timedelta(minutes=event.fail_minutes)

        # 현재 시간이 absent_time을 지났는지 확인
        if now < absent_time:
            continue

        logger.info(f"Processing event: {event.title} (ID: {event.id})")
        processed_events += 1

        # 해당 세대에 속한 모든 멤버 가져오기
        gen_members = GenMember.objects.filter(
            generation=event.generation, is_current=True
        )

        # 이미 출석 상태가 있는 멤버 ID 목록
        existing_attendance_member_ids = Attendance.objects.filter(
            event=event
        ).values_list("generation_mapping_id", flat=True)

        # 출석 전 상태인 멤버들 결석으로 변경
        unchecked_attendances = Attendance.objects.filter(
            event=event, status=AttendanceStatus.UNCHECKED
        )

        update_count = unchecked_attendances.update(
            status=AttendanceStatus.ABSENT, is_modified=True, modified_at=now
        )
        total_updated += update_count

        logger.info(f"Updated {update_count} unchecked attendances to absent")

        # 출석 상태가 없는 멤버들에 대해 결석 상태로 생성
        new_attendances = []
        for gen_member in gen_members:
            if gen_member.id not in existing_attendance_member_ids:
                new_attendances.append(
                    Attendance(
                        generation_mapping=gen_member,
                        event=event,
                        status=AttendanceStatus.ABSENT,
                        is_modified=True,
                        modified_at=now,
                    )
                )

        if new_attendances:
            Attendance.objects.bulk_create(new_attendances)
            total_created += len(new_attendances)
            logger.info(f"Created {len(new_attendances)} new absent attendances")

    logger.info(
        f"Completed mark_absent_for_past_events job - Processed {processed_events} events, Updated {total_updated} attendances, Created {total_created} new attendances"
    )

    return {
        "processed_events": processed_events,
        "updated_attendances": total_updated,
        "created_attendances": total_created,
    }
