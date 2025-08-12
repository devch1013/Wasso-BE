import os

from celery import Celery
from celery.schedules import crontab

# Django 설정 모듈 설정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.django.dev")

app = Celery("wasso")

# Django 설정을 사용하여 Celery 구성
app.config_from_object("django.conf:settings", namespace="CELERY")

# 자동으로 Django 앱에서 tasks.py 파일을 찾아서 등록
app.autodiscover_tasks()

# 스케줄러 설정
app.conf.beat_schedule = {
    "mark-absent-for-past-events": {
        "task": "scheduler.tasks.mark_absent_for_past_events",
        "schedule": 300.0,  # 5분마다 실행
    },
    "event-start-push-test": {
        "task": "scheduler.tasks.event_start_push_test",
        "schedule": crontab(
            minute="*/5"
        ),  # 매 시간의 0,5,10,15,20,25,30,35,40,45,50,55분에 실행
    },
}

app.conf.timezone = "Asia/Seoul"


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
