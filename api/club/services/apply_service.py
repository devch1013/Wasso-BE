from django.db import transaction
from django.utils import timezone

from api.club.models import ClubApply, Generation, GenerationMapping, Member
from common.exceptions import CustomException, ErrorCode
from api.userapp.models import User


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

    @staticmethod
    @transaction.atomic
    def approve_apply(apply_id: int):
        club_apply = ClubApply.objects.filter(id=apply_id, accepted=False).first()
        if not club_apply:
            raise CustomException(ErrorCode.APPLY_NOT_FOUND)

        if Member.objects.filter(
            user=club_apply.user, club=club_apply.generation.club
        ).exists():
            raise CustomException(ErrorCode.ALREADY_APPLIED)

        member = Member.objects.create(
            user=club_apply.user,
            club=club_apply.generation.club,
        )

        GenerationMapping.objects.create(
            member=member,
            generation=club_apply.generation,
            role=club_apply.generation.club.default_role,
            is_current=True,
        )

        club_apply.accepted = True
        club_apply.accepted_at = timezone.now()
        club_apply.save()
        return club_apply

    @staticmethod
    def reject_apply(apply_id: int):
        club_apply = ClubApply.objects.filter(id=apply_id, accepted=False).first()
        if not club_apply:
            raise CustomException(ErrorCode.APPLY_NOT_FOUND)
        club_apply.delete()
