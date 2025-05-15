from django.db.models import Count, Case, When, IntegerField
from django.db.models import F

from api.club.models import GenMember, Generation
from common.utils.notion import NotionAttendanceManager
from api.userapp.models import User


class GenerationService:
    @staticmethod
    def get_generation_stats(generation_id: int) -> list[GenMember]:
        generation = Generation.objects.get(id=generation_id)

        # Get all generation mappings and their members
        stats = (
            GenMember.objects.filter(generation=generation)
            .select_related("member__user")
            .prefetch_related("attendances")
            .annotate(
                present_count=Count(
                    Case(
                        When(attendances__status=1, then=1),
                        output_field=IntegerField(),
                    )
                ),
                late_count=Count(
                    Case(
                        When(attendances__status=2, then=1),
                        output_field=IntegerField(),
                    )
                ),
                absent_count=Count(
                    Case(
                        When(attendances__status=3, then=1),
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
        generation: Generation, notion_database_id: str, user: User = None
    ):
        # Extract database_id from Notion URL if full URL is provided
        if notion_database_id.startswith('https://'):
            # Extract the ID part from the URL
            # Format: https://www.notion.so/username/database_id?v=...
            parts = notion_database_id.split('/')
            for part in parts:
                if '?' in part:
                    notion_database_id = part.split('?')[0]
                    break
                elif len(part) == 32 or '-' in part and len(part.replace('-', '')) == 32:
                    notion_database_id = part
                    break
        
        notion_db = NotionAttendanceManager()
        return notion_db.update_attendance_database_async(
            generation,
            database_id=notion_database_id,
            user=user
        )

    @staticmethod
    def activate_generation(generation: Generation):
        generations = Generation.objects.filter(club=generation.club)
        for gen in generations:
            if gen.activated:   
                gen.activated = False
                gen.save()
        generation.activated = True
        generation.save()
        club = generation.club
        club.current_generation = generation
        club.save()
        return generation
