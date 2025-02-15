from django.db import transaction
from django.utils import timezone

from api.club.models import ClubApply, Generation, GenerationMapping, Member
from config.exceptions import CustomException, ErrorCode
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
    def approve_apply(apply_ids: list[int]):
        print(apply_ids)
        club_applies = ClubApply.objects.filter(id__in=apply_ids, accepted=False)
        print(club_applies)
        user_generations = []
        members = []
        for club_apply in club_applies:
            if Member.objects.filter(
                user=club_apply.user, club=club_apply.generation.club
            ).exists():
                continue
            members.append(
                Member(
                    user=club_apply.user,
                    club=club_apply.generation.club,
                )
            )
        Member.objects.bulk_create(members)
        for club_apply in club_applies:
            user_generations.append(
                GenerationMapping(
                    member=Member.objects.get(
                        user=club_apply.user, club=club_apply.generation.club
                    ),
                    generation=club_apply.generation,
                    role=club_apply.generation.club.default_role,
                    is_current=True,
                )
            )

        GenerationMapping.objects.bulk_create(user_generations)

        club_applies.update(accepted=True, accepted_at=timezone.now())
        return club_applies
