from django.db import transaction
from django.utils import timezone

from api.club.models import ClubApply, Generation, GenMember, Member
from common.exceptions import CustomException, ErrorCode
from api.userapp.models import User
from common.component.user_selector import UserSelector
from common.component.fcm_component import FCMComponent
from common.component.notification_template import NotificationTemplate
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
        if GenMember.objects.filter(
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
            NotificationTemplate.CLUB_APPLY.get_title(),
            NotificationTemplate.CLUB_APPLY.get_body(username = user.username),
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
            NotificationTemplate.CLUB_APPLY_ACCEPT.get_title(club_name = club_apply.generation.club.name),
            NotificationTemplate.CLUB_APPLY_ACCEPT.get_body(club_name = club_apply.generation.club.name),
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
            NotificationTemplate.CLUB_APPLY_REJECT.get_title(club_name = club_apply.generation.club.name),
            NotificationTemplate.CLUB_APPLY_REJECT.get_body(club_name = club_apply.generation.club.name),
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

        generation_mapping = GenMember.objects.create(
            member=member,
            generation=generation,
            role=generation.club.default_role,
            is_current=True,
        )

        return member, generation_mapping