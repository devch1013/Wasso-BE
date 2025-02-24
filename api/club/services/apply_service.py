from django.db import transaction
from django.utils import timezone

from api.club.models import ClubApply, Generation, GenerationMapping, Member
from common.exceptions import CustomException, ErrorCode
from api.userapp.models import User
from common.component.user_selector import UserSelector
from common.component.fcm_component import FCMComponent
from loguru import logger

fcm_component = FCMComponent()

class ApplyService:
    @staticmethod
    def apply(user: User, club_code: str):
        if not club_code:
            raise CustomException(ErrorCode.PARAMS_MISSING)
        generation = Generation.objects.filter(invite_code=club_code).first()
        if not generation:
            raise CustomException(ErrorCode.GENERATION_NOT_FOUND)
        if GenerationMapping.objects.filter(
            member__user=user, generation=generation
        ).exists():
            raise CustomException(ErrorCode.ALREADY_APPLIED)
        if ClubApply.objects.filter(user=user, generation=generation).exists():
            raise CustomException(ErrorCode.ALREADY_APPLIED)
        ClubApply.objects.create(user=user, generation=generation)
        
        notice_users = UserSelector.get_users_by_role(
            generation=generation,
            signup_accept=True,
        )
        result = fcm_component.send_to_users(
            notice_users,
            "동아리 가입 신청",
            f"{user.username}님이 {generation.club.name} 동아리에 가입을 요청했습니다.",
        )
        logger.info(result)

    @staticmethod
    @transaction.atomic
    def approve_apply(apply_id: int):
        club_apply = ClubApply.objects.filter(id=apply_id, accepted=False).first()
        if not club_apply:
            raise CustomException(ErrorCode.APPLY_NOT_FOUND)

        member, generation_mapping = ApplyService.join_generation(
            club_apply.user, club_apply.generation
        )

        club_apply.accepted = True
        club_apply.accepted_at = timezone.now()
        club_apply.save()
        
        fcm_component.send_to_user(
            club_apply.user,
            f"[{club_apply.generation.club.name}] 가입 신청",
            f"{club_apply.generation.club.name} 가입이 수락되었습니다.",
        )
        
        return member, generation_mapping

    @staticmethod
    def reject_apply(apply_id: int):
        club_apply = ClubApply.objects.filter(id=apply_id, accepted=False).first()
        if not club_apply:
            raise CustomException(ErrorCode.APPLY_NOT_FOUND)
        club_apply.delete()
        fcm_component.send_to_user(
            club_apply.user,
            f"[{club_apply.generation.club.name}] 가입 신청",
            f"{club_apply.generation.club.name} 가입이 거절되었습니다.",
        )
        
    @staticmethod
    def join_generation(user: User, generation: Generation):
        if Member.objects.filter(
            user=user, club=generation.club
        ).exists():
            raise CustomException(ErrorCode.ALREADY_APPLIED)

        member = Member.objects.create(
            user=user,
            club=generation.club,
        )

        generation_mapping = GenerationMapping.objects.create(
            member=member,
            generation=generation,
            role=generation.club.default_role,
            is_current=True,
        )

        return member, generation_mapping