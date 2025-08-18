import logging

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from api.userapp.models.user import User
from api.userapp.models.user_meta import FcmToken

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "User 모델의 fcm_token 필드를 FcmToken 모델로 안전하게 마이그레이션합니다."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="실제 마이그레이션 없이 시뮬레이션만 수행",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1000,
            help="한 번에 처리할 레코드 수 (기본값: 1000)",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="이미 마이그레이션된 데이터가 있어도 강제로 실행",
        )
        parser.add_argument(
            "--cleanup",
            action="store_true",
            help="마이그레이션 완료 후 User 모델의 fcm_token 필드 데이터 정리",
        )

    def handle(self, *args, **options):
        """FCM 토큰 마이그레이션 메인 처리 함수"""

        dry_run = options["dry_run"]
        batch_size = options["batch_size"]
        force = options["force"]
        cleanup = options["cleanup"]

        # 로깅 설정
        self.setup_logging()

        self.stdout.write(
            self.style.SUCCESS(
                f"{'[DRY RUN] ' if dry_run else ''}FCM 토큰 마이그레이션을 시작합니다..."
            )
        )

        try:
            # 사전 검증
            self.pre_migration_checks(force)

            # 마이그레이션 통계 수집
            stats = self.collect_migration_stats()
            self.display_migration_stats(stats)

            # 사용자 확인 (dry-run이 아닌 경우)
            if not dry_run and not self.confirm_migration(stats):
                self.stdout.write(self.style.WARNING("마이그레이션이 취소되었습니다."))
                return

            # 마이그레이션 실행
            migrated_count = self.migrate_fcm_tokens(dry_run, batch_size)

            # 정리 작업 (cleanup 옵션이 활성화된 경우)
            if cleanup and not dry_run and migrated_count > 0:
                self.cleanup_old_tokens(batch_size)

            # 완료 메시지
            self.stdout.write(
                self.style.SUCCESS(
                    f"{'[DRY RUN] ' if dry_run else ''}마이그레이션이 완료되었습니다. "
                    f"총 {migrated_count}개의 FCM 토큰이 처리되었습니다."
                )
            )

        except Exception as e:
            logger.error(f"마이그레이션 중 오류 발생: {str(e)}")
            self.stdout.write(
                self.style.ERROR(f"마이그레이션 중 오류가 발생했습니다: {str(e)}")
            )
            raise CommandError(f"마이그레이션 실패: {str(e)}")

    def setup_logging(self):
        """로깅 설정"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    def pre_migration_checks(self, force):
        """마이그레이션 전 검증"""
        self.stdout.write("사전 검증을 수행합니다...")

        # FcmToken 테이블 존재 확인
        try:
            FcmToken.objects.exists()
        except Exception as e:
            raise CommandError(
                f"FcmToken 모델에 접근할 수 없습니다. 마이그레이션을 먼저 실행하세요: {str(e)}"
            )

        # 이미 마이그레이션된 데이터 확인
        existing_fcm_tokens = FcmToken.objects.count()
        if existing_fcm_tokens > 0 and not force:
            raise CommandError(
                f"이미 {existing_fcm_tokens}개의 FCM 토큰이 FcmToken 테이블에 존재합니다. "
                "강제로 실행하려면 --force 옵션을 사용하세요."
            )

        self.stdout.write(self.style.SUCCESS("✓ 사전 검증 완료"))

    def collect_migration_stats(self):
        """마이그레이션 통계 수집"""
        stats = {
            "total_users": User.objects.count(),
            "users_with_fcm_token": User.objects.exclude(fcm_token__isnull=True)
            .exclude(fcm_token="")
            .count(),
            "users_without_fcm_token": User.objects.filter(
                fcm_token__isnull=True
            ).count()
            + User.objects.filter(fcm_token="").count(),
            "existing_fcm_tokens": FcmToken.objects.count(),
        }
        return stats

    def display_migration_stats(self, stats):
        """마이그레이션 통계 표시"""
        self.stdout.write("\n=== 마이그레이션 통계 ===")
        self.stdout.write(f"전체 사용자 수: {stats['total_users']}")
        self.stdout.write(f"FCM 토큰이 있는 사용자: {stats['users_with_fcm_token']}")
        self.stdout.write(f"FCM 토큰이 없는 사용자: {stats['users_without_fcm_token']}")
        self.stdout.write(f"기존 FcmToken 레코드: {stats['existing_fcm_tokens']}")
        self.stdout.write("========================\n")

    def confirm_migration(self, stats):
        """마이그레이션 확인"""
        if stats["users_with_fcm_token"] == 0:
            self.stdout.write(self.style.WARNING("마이그레이션할 FCM 토큰이 없습니다."))
            return False

        self.stdout.write(
            f"{stats['users_with_fcm_token']}개의 FCM 토큰을 마이그레이션하시겠습니까?"
        )

        while True:
            response = input("계속하시겠습니까? [y/N]: ").lower().strip()
            if response in ["y", "yes"]:
                return True
            elif response in ["n", "no", ""]:
                return False
            else:
                self.stdout.write("'y' 또는 'n'을 입력해주세요.")

    def migrate_fcm_tokens(self, dry_run, batch_size):
        """FCM 토큰 마이그레이션 실행"""
        self.stdout.write("FCM 토큰 마이그레이션을 시작합니다...")

        # FCM 토큰이 있는 사용자들을 배치로 처리
        users_with_tokens = User.objects.exclude(fcm_token__isnull=True).exclude(
            fcm_token=""
        )
        total_count = users_with_tokens.count()
        migrated_count = 0

        self.stdout.write(f"총 {total_count}개의 FCM 토큰을 처리합니다.")

        for i in range(0, total_count, batch_size):
            batch_users = users_with_tokens[i : i + batch_size]
            batch_migrated = self.process_batch(batch_users, dry_run)
            migrated_count += batch_migrated

            # 진행상황 표시
            progress = min(i + batch_size, total_count)
            self.stdout.write(
                f"진행: {progress}/{total_count} ({progress/total_count*100:.1f}%)"
            )

        return migrated_count

    def process_batch(self, users, dry_run):
        """배치 단위로 FCM 토큰 처리"""
        migrated_count = 0

        if dry_run:
            # DRY RUN: 실제 저장하지 않고 시뮬레이션만
            for user in users:
                if self.should_migrate_user_token(user):
                    migrated_count += 1
                    logger.info(
                        f"[DRY RUN] User {user.id}의 FCM 토큰 '{user.fcm_token}' 마이그레이션 예정"
                    )
        else:
            # 실제 마이그레이션 실행
            with transaction.atomic():
                try:
                    for user in users:
                        if self.should_migrate_user_token(user):
                            fcm_token = self.create_fcm_token(user)
                            if fcm_token:
                                migrated_count += 1
                                logger.info(
                                    f"User {user.id}의 FCM 토큰이 마이그레이션되었습니다."
                                )

                except Exception as e:
                    logger.error(f"배치 처리 중 오류 발생: {str(e)}")
                    raise

        return migrated_count

    def should_migrate_user_token(self, user):
        """사용자의 FCM 토큰을 마이그레이션해야 하는지 확인"""
        # FCM 토큰이 없으면 스킵
        if not user.fcm_token or user.fcm_token.strip() == "":
            return False

        # 이미 해당 사용자의 FCM 토큰이 존재하는지 확인
        existing_token = FcmToken.objects.filter(
            user=user, token=user.fcm_token, active=True
        ).exists()

        return not existing_token

    def create_fcm_token(self, user):
        """FcmToken 객체 생성"""
        try:
            fcm_token, created = FcmToken.objects.get_or_create(
                user=user,
                token=user.fcm_token,
                defaults={
                    "active": True,
                },
            )

            if created:
                logger.info(
                    f"새로운 FcmToken 생성: User {user.id}, Token {user.fcm_token}"
                )
            else:
                logger.info(
                    f"기존 FcmToken 발견: User {user.id}, Token {user.fcm_token}"
                )

            return fcm_token

        except Exception as e:
            logger.error(f"FcmToken 생성 실패 - User {user.id}: {str(e)}")
            return None

    def cleanup_old_tokens(self, batch_size):
        """기존 User 모델의 fcm_token 필드 정리"""
        self.stdout.write("기존 FCM 토큰 필드를 정리합니다...")

        # 마이그레이션된 토큰이 있는 사용자들의 fcm_token 필드를 null로 설정
        users_with_migrated_tokens = (
            User.objects.filter(fcmtoken__isnull=False, fcmtoken__active=True)
            .exclude(fcm_token__isnull=True)
            .exclude(fcm_token="")
        )

        total_count = users_with_migrated_tokens.count()
        cleaned_count = 0

        self.stdout.write(f"총 {total_count}개의 사용자 FCM 토큰 필드를 정리합니다.")

        for i in range(0, total_count, batch_size):
            batch_users = users_with_migrated_tokens[i : i + batch_size]

            with transaction.atomic():
                for user in batch_users:
                    # 해당 사용자의 활성화된 FcmToken이 존재하는지 확인
                    if FcmToken.objects.filter(
                        user=user, token=user.fcm_token, active=True
                    ).exists():
                        user.fcm_token = None
                        user.save(update_fields=["fcm_token", "updated_at"])
                        cleaned_count += 1
                        logger.info(
                            f"User {user.id}의 fcm_token 필드가 정리되었습니다."
                        )

            # 진행상황 표시
            progress = min(i + batch_size, total_count)
            self.stdout.write(
                f"정리 진행: {progress}/{total_count} ({progress/total_count*100:.1f}%)"
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"총 {cleaned_count}개의 fcm_token 필드가 정리되었습니다."
            )
        )
