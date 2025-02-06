from django.db import transaction
from django.utils import timezone

from club.models import ClubApply, Generation, GenerationMapping, Member
from main.exceptions import CustomException, ErrorCode
from userapp.models import User


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
    def approve_apply(apply_ids: list[int]):
        club_applies = ClubApply.objects.filter(id__in=apply_ids, accepted=False)
        user_generations = []
        members = []
        user_clubs = []
        for club_apply in club_applies:
            members.append(
                Member(
                    user=club_apply.user,
                    club=club_apply.generation.club,
                    last_user_generation=club_apply.generation,
                )
            )
            user_generations.append(
                GenerationMapping(
                    user=club_apply.user, generation=club_apply.generation
                )
            )
        GenerationMapping.objects.bulk_create(user_generations)
        for idx, club_apply in enumerate(club_applies):
            user_clubs.append(
                Member(
                    user=club_apply.user,
                    club=club_apply.generation.club,
                    last_user_generation=user_generations[idx],
                )
            )
        Member.objects.bulk_create(user_clubs)
        club_applies.update(accepted=True, accepted_at=timezone.now())
        return club_applies
