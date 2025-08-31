from django.db import transaction
from loguru import logger

from api.club.models import ClubApply, Generation, GenMember, Member
from api.userapp.models import User
from common.component.fcm_component import FCMComponent
from common.component.notification_template import NotificationTemplate
from common.component.user_selector import UserSelector
from common.exceptions import CustomException, ErrorCode

fcm_component = FCMComponent()


class ApplyService:
    @classmethod
    def get_generation_from_code(cls, code: str):
        generation = Generation.objects.filter(invite_code=code).first()
        if not generation:
            raise CustomException(ErrorCode.GENERATION_NOT_FOUND)
        return generation

    @classmethod
    def apply(cls, user: User, club_code: str):
        if not club_code:
            raise CustomException(ErrorCode.PARAMS_MISSING)
        generation = Generation.objects.filter(invite_code=club_code).first()
        if not generation:
            raise CustomException(ErrorCode.GENERATION_NOT_FOUND)
        if GenMember.objects.filter(member__user=user, generation=generation).exists():
            raise CustomException(ErrorCode.ALREADY_APPLIED)
        if ClubApply.objects.filter(user=user, generation=generation).exists():
            raise CustomException(ErrorCode.ALREADY_APPLIED)

        if generation.auto_approve:
            cls.join_generation(user, generation)
            return

        ClubApply.objects.create(user=user, generation=generation)

        notice_users = UserSelector.get_users_by_role(
            generation=generation,
            signup_accept=True,
        )
        result = fcm_component.send_to_users(
            notice_users,
            NotificationTemplate.CLUB_APPLY.get_title(),
            NotificationTemplate.CLUB_APPLY.get_body(username=user.username),
            data=NotificationTemplate.CLUB_APPLY.get_deeplink_data(),
        )
        logger.info(result)

    @classmethod
    @transaction.atomic
    def approve_apply(cls, apply_id: int):
        club_apply: ClubApply = ClubApply.objects.filter(
            id=apply_id, accepted=False
        ).first()
        if not club_apply:
            raise CustomException(ErrorCode.APPLY_NOT_FOUND)

        cls.approve_apply_instance(club_apply)
        return

    @classmethod
    def approve_apply_instance(cls, club_apply: ClubApply):
        cls.join_generation(club_apply.user, club_apply.generation)

        club_apply.accept()

        fcm_component.send_to_user(
            club_apply.user,
            NotificationTemplate.CLUB_APPLY_ACCEPT.get_title(
                club_name=club_apply.generation.club.name
            ),
            NotificationTemplate.CLUB_APPLY_ACCEPT.get_body(
                club_name=club_apply.generation.club.name
            ),
            data=NotificationTemplate.CLUB_APPLY_ACCEPT.get_deeplink_data(),
        )

        return

    @classmethod
    def apply_all(cls, generation: Generation):
        club_applies = ClubApply.objects.filter(generation=generation, accepted=False)
        ## TODO: bulk 처리 추가
        for club_apply in club_applies:
            cls.approve_apply_instance(club_apply)

    @classmethod
    def reject_apply(cls, apply_id: int):
        club_apply = ClubApply.objects.filter(id=apply_id, accepted=False).first()
        if not club_apply:
            raise CustomException(ErrorCode.APPLY_NOT_FOUND)
        club_apply.delete()
        fcm_component.send_to_user(
            club_apply.user,
            NotificationTemplate.CLUB_APPLY_REJECT.get_title(
                club_name=club_apply.generation.club.name
            ),
            NotificationTemplate.CLUB_APPLY_REJECT.get_body(
                club_name=club_apply.generation.club.name
            ),
            data=NotificationTemplate.CLUB_APPLY_REJECT.get_deeplink_data(),
        )

    @classmethod
    def join_generation(cls, user: User, generation: Generation):
        ## 이미 가입되어있으면 넘어가기
        existed_gen_member = GenMember.objects.filter(
            member__user=user, generation=generation
        )
        if existed_gen_member.exists():
            return existed_gen_member.first().member, existed_gen_member.first()

        existed_member = Member.objects.filter(user=user, club=generation.club).first()
        if existed_member:
            existed_member.restore()
            member = existed_member
        else:
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
