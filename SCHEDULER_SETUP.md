# Wasso 프로젝트 스케줄러 설정 가이드

## 개요
이 프로젝트에는 Celery와 Redis를 사용한 스케줄러가 설정되어 있습니다. 현재 설정된 주요 기능은 출석 관리 자동화입니다.

## 필요한 패키지
프로젝트에 다음 패키지들이 추가되었습니다:
- `celery`: 분산 작업 큐
- `django-celery-beat`: Django와 Celery 스케줄러 통합
- `redis`: 메시지 브로커 및 결과 백엔드

## 설정 완료된 항목들

### 1. Celery 설정
- `config/celery.py`: Celery 앱 설정
- `config/__init__.py`: Django와 Celery 연동 설정
- `config/django/base.py`: Django 설정에 Celery 관련 설정 추가

### 2. 스케줄된 작업
- `scheduler/tasks.py`: 출석 관리 자동화 작업
  - `mark_absent_for_past_events`: 이벤트 시간 경과 후 미출석자를 결석으로 처리

### 3. 관리 명령어
- `scheduler/management/commands/setup_periodic_tasks.py`: 주기적 작업 설정 명령어

## 실행 방법

### 1. 의존성 설치
```bash
poetry install
```

### 2. 데이터베이스 마이그레이션
```bash
python manage.py migrate
```

### 3. 주기적 작업 설정
```bash
python manage.py setup_periodic_tasks
```

### 4. Redis 서버 시작 (별도 터미널)
```bash
redis-server
```

### 5. Celery Worker 시작 (별도 터미널)
```bash
chmod +x scripts/start_celery_worker.sh
./scripts/start_celery_worker.sh
```

또는 직접 명령어로:
```bash
celery -A config worker --loglevel=info --concurrency=4
```

### 6. Celery Beat 스케줄러 시작 (별도 터미널)
```bash
chmod +x scripts/start_celery_beat.sh
./scripts/start_celery_beat.sh
```

또는 직접 명령어로:
```bash
celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

## 현재 설정된 스케줄

### mark_absent_for_past_events
- **실행 주기**: 5분마다
- **기능**: 이벤트 시작 시간 + fail_minutes가 지난 이벤트에 대해
  - UNCHECKED 상태인 출석을 ABSENT로 변경
  - 출석 기록이 없는 멤버들에 대해 ABSENT 상태로 생성

## 스케줄 관리

### Django Admin에서 관리
1. Django admin에 로그인
2. DJANGO CELERY BEAT 섹션에서 스케줄 관리 가능
   - Periodic tasks: 주기적 작업 목록
   - Intervals: 실행 간격 설정
   - Crontabs: cron 스타일 스케줄 설정

### 프로그래밍 방식으로 관리
```python
from django_celery_beat.models import PeriodicTask, IntervalSchedule

# 새로운 스케줄 생성
schedule = IntervalSchedule.objects.create(
    every=10,
    period=IntervalSchedule.MINUTES,
)

# 새로운 주기적 작업 생성
PeriodicTask.objects.create(
    interval=schedule,
    name='My periodic task',
    task='myapp.tasks.my_task',
)
```

## 모니터링

### Celery 작업 상태 확인
```bash
# 활성 작업 확인
celery -A config inspect active

# 등록된 작업 확인
celery -A config inspect registered

# 스케줄된 작업 확인
celery -A config inspect scheduled
```

### 로그 확인
- Celery worker와 beat의 로그를 통해 작업 실행 상태를 모니터링할 수 있습니다.
- Django의 logging 설정에 따라 로그가 기록됩니다.

## 추가 작업 생성

새로운 스케줄된 작업을 추가하려면:

1. `scheduler/tasks.py`에 새로운 `@shared_task` 함수 추가
2. `setup_periodic_tasks.py`에 새로운 작업 등록 코드 추가
3. `python manage.py setup_periodic_tasks` 실행

## 주의사항

1. **Redis 서버**: Celery가 작동하려면 Redis 서버가 실행 중이어야 합니다.
2. **Worker 프로세스**: 작업이 실행되려면 최소 하나의 Celery worker가 실행 중이어야 합니다.
3. **Beat 스케줄러**: 주기적 작업이 예약되려면 Celery beat가 실행 중이어야 합니다.
4. **데이터베이스**: django-celery-beat는 스케줄 정보를 Django 데이터베이스에 저장합니다.

## 프로덕션 배포 시 고려사항

1. **Supervisor/Systemd**: Celery 프로세스를 서비스로 관리
2. **로그 로테이션**: Celery 로그 파일 관리
3. **모니터링**: Flower나 다른 모니터링 도구 사용 고려
4. **확장성**: worker 수를 서버 리소스에 맞게 조정 