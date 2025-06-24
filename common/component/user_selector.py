from api.club.models import Generation, GenMember


class UserSelector:
    def __init__(self):
        pass

    @staticmethod
    def get_users_by_role(
        generation: Generation,
        role_manage: bool | None = None,
        event_manage: bool | None = None,
        member_manage: bool | None = None,
        signup_accept: bool | None = None,
        club_info_manage: bool | None = None,
        generation_change: bool | None = None,
        attendance_manage: bool | None = None,
    ):
        # Get all generation mappings for the given generation
        mappings = GenMember.objects.filter(
            generation=generation, is_current=True
        ).select_related("member__user", "role")

        if not mappings:
            return []

        # Build role filter conditions
        role_conditions = {}
        if role_manage is not None:
            role_conditions["role__role_manage"] = role_manage
        if event_manage is not None:
            role_conditions["role__event_manage"] = event_manage
        if member_manage is not None:
            role_conditions["role__member_manage"] = member_manage
        if signup_accept is not None:
            role_conditions["role__signup_accept"] = signup_accept
        if club_info_manage is not None:
            role_conditions["role__club_info_manage"] = club_info_manage
        if generation_change is not None:
            role_conditions["role__generation_change"] = generation_change
        if attendance_manage is not None:
            role_conditions["role__attendance_manage"] = attendance_manage

        # Filter mappings based on role conditions
        if role_conditions:
            mappings = mappings.filter(**role_conditions)

        # Return list of users
        return [mapping.member.user for mapping in mappings]

    @staticmethod
    def get_users_by_generation(generation: Generation):
        mappings = GenMember.objects.filter(generation=generation).select_related(
            "member__user"
        )
        return [mapping.member.user for mapping in mappings]
