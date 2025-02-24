from django.db.models import Count, Case, When, IntegerField
from django.db.models import F

from api.club.models import GenerationMapping, Generation


class GenerationService:
    @staticmethod
    def get_generation_stats(generation_id: int) -> list[GenerationMapping]:
        generation = Generation.objects.get(id=generation_id)
        
        # Get all generation mappings and their members
        stats = GenerationMapping.objects.filter(
            generation=generation
        ).select_related('member__user').prefetch_related('attendance_set').annotate(
            present_count=Count(
                Case(
                    When(attendance__status=1, then=1),
                    output_field=IntegerField(),
                )
            ),
            late_count=Count(
                Case(
                    When(attendance__status=2, then=1),
                    output_field=IntegerField(),
                )
            ),
            absent_count=Count(
                Case(
                    When(attendance__status=3, then=1),
                    output_field=IntegerField(),
                )
            ),
            member_name=F('member__user__username')
        ).order_by('member_name')
        
        return stats