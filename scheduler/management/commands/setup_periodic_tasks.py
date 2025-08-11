import json

from django.core.management.base import BaseCommand
from django_celery_beat.models import IntervalSchedule, PeriodicTask


class Command(BaseCommand):
    help = "Setup periodic tasks for the scheduler"

    def handle(self, *args, **options):
        # 5분마다 실행되는 스케줄 생성 또는 가져오기
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=5,
            period=IntervalSchedule.MINUTES,
        )

        # 기존 작업이 있다면 삭제
        PeriodicTask.objects.filter(name="Mark absent for past events").delete()

        # 새로운 주기적 작업 생성
        PeriodicTask.objects.create(
            interval=schedule,
            name="Mark absent for past events",
            task="scheduler.tasks.mark_absent_for_past_events",
            args=json.dumps([]),
            kwargs=json.dumps({}),
            enabled=True,
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully setup periodic task: Mark absent for past events (every 5 minutes)"
            )
        )
