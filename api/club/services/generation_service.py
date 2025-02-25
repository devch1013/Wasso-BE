from django.db.models import Count, Case, When, IntegerField
from django.db.models import F

from api.club.models import GenMember, Generation
from common.utils.notion import NotionAttendanceManager


class GenerationService:
    @staticmethod
    def get_generation_stats(generation_id: int) -> list[GenMember]:
        generation = Generation.objects.get(id=generation_id)

        # Get all generation mappings and their members
        stats = (
            GenMember.objects.filter(generation=generation)
            .select_related("member__user")
            .prefetch_related("attendance_set")
            .annotate(
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
                member_name=F("member__user__username"),
            )
            .order_by("member_name")
        )

        return stats

    @staticmethod
    def update_notion(
        generation: Generation, notion_page_id: str, notion_database_id: str
    ):
        notion_db = NotionAttendanceManager()
        notion_db.update_attendance_database(
            generation,
            page_id=notion_page_id,
            database_id=notion_database_id,
        )
