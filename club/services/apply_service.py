from django.db import transaction
from django.utils import timezone

from club.models import ClubApply, GenerationMapping, Member


class ApplyService:
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
