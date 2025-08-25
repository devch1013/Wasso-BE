from django.db.models import Case, Count, F, IntegerField, OuterRef, Subquery, When

from api.club.models import Generation, GenMember
from api.club.models.member import Member
from api.event.models import Attendance
from api.userapp.models import User
from common.utils.notion import NotionAttendanceManager


class GenerationService:
    @staticmethod
    def get_generation_stats(generation_id: int) -> list[GenMember]:
        generation = Generation.objects.get(id=generation_id)

        # Get all generation mappings and their members
        stats = (
            GenMember.objects.filter(generation=generation)
            .select_related("member__user")
            .annotate(
                present_count=Count(
                    Case(
                        When(
                            attendances__created_at=Subquery(
                                Attendance.objects.filter(
                                    generation_mapping=OuterRef("id"),
                                    event=OuterRef("attendances__event"),
                                )
                                .order_by("-created_at")
                                .values("created_at")[:1]
                            ),
                            attendances__status=1,
                            then=1,
                        ),
                        output_field=IntegerField(),
                    )
                ),
                late_count=Count(
                    Case(
                        When(
                            attendances__created_at=Subquery(
                                Attendance.objects.filter(
                                    generation_mapping=OuterRef("id"),
                                    event=OuterRef("attendances__event"),
                                )
                                .order_by("-created_at")
                                .values("created_at")[:1]
                            ),
                            attendances__status=2,
                            then=1,
                        ),
                        output_field=IntegerField(),
                    )
                ),
                absent_count=Count(
                    Case(
                        When(
                            attendances__created_at=Subquery(
                                Attendance.objects.filter(
                                    generation_mapping=OuterRef("id"),
                                    event=OuterRef("attendances__event"),
                                )
                                .order_by("-created_at")
                                .values("created_at")[:1]
                            ),
                            attendances__status=3,
                            then=1,
                        ),
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
        if notion_database_id.startswith("https://"):
            # Extract the ID part from the URL
            # Format: https://www.notion.so/username/database_id?v=...
            parts = notion_database_id.split("/")
            for part in parts:
                if "?" in part:
                    notion_database_id = part.split("?")[0]
                    break
                elif (
                    len(part) == 32 or "-" in part and len(part.replace("-", "")) == 32
                ):
                    notion_database_id = part
                    break

        notion_db = NotionAttendanceManager()
        return notion_db.update_attendance_database_async(
            generation, database_id=notion_database_id, user=user
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

        return Generation.objects.filter(club=generation.club)

    @classmethod
    def toggle_auto_approve(cls, generation: Generation):
        generation.auto_approve = not generation.auto_approve
        generation.save()
        return generation

    @classmethod
    def get_generations_by_member(cls, member: Member):
        generation_ids = member.gen_members.values_list("generation_id", flat=True)
        return Generation.objects.filter(id__in=generation_ids).order_by("start_date")

    @classmethod
    def get_generations_by_user(cls, user: User, club_id: int):
        member = Member.objects.get(user=user, club__id=club_id)
        return cls.get_generations_by_member(member)

    @classmethod
    def get_all_generations_of_club(cls, club_id: int):
        return Generation.objects.filter(club__id=club_id).order_by("start_date")
