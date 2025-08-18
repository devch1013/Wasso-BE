# 1. 시뮬레이션으로 먼저 확인
python manage.py fcm_migration --dry-run

# 2. 실제 마이그레이션 실행
python manage.py fcm_migration

# 3. 기존 필드 정리까지 포함
python manage.py fcm_migration --cleanup

# 4. 강제 실행 (기존 데이터 무시)
python manage.py fcm_migration --force

# 5. 배치 크기 조정
python manage.py fcm_migration --batch-size 500