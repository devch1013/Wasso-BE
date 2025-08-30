import random
import string

from django.db import transaction

from api.club.models import Club, Generation, GenMember, Member, Role
from api.userapp.models import User
from common.exceptions import CustomException, ErrorCode


class ClubService:
    @staticmethod
    @transaction.atomic
    def create_club(
        user: User,
        name: str,
        image,
        description: str,
        short_description: str,
        generation_data: dict,
    ):
        print("clubName", name)
        if Club.objects.filter(name=name).exists():
            raise CustomException(ErrorCode.CLUB_ALREADY_EXISTS)

        club = Club.objects.create(
            name=name,
            image=image,
            description=description,
            short_description=short_description,
        )

        invite_code = "".join(random.choices(string.digits, k=6))

        # 첫 번째 기수(generation) 생성
        generation = Generation.objects.create(
            club=club, **generation_data, invite_code=invite_code, activated=True
        )

        owner_role = Role.create_owner_role(club)
        Role.create_admin_role(club)
        member_role = Role.create_member_role(club)

        club.default_role = member_role
        club.current_generation = generation
        club.save()

        member = Member.objects.create(
            user=user,
            club=club,
        )

        # 생성자를 owner로 추가
        GenMember.objects.create(
            member=member,
            generation=generation,
            role=owner_role,
            is_current=True,
        )

        return club, member

    @staticmethod
    def create_generation(
        club: Club, generation_data: dict, user: User
    ) -> list[Generation]:
        invite_code = "".join(random.choices(string.digits, k=6))
        generation = Generation.objects.create(
            club=club, **generation_data, invite_code=invite_code
        )
        member = Member.objects.get(user=user, club=club)
        GenMember.objects.create(
            member=member,
            generation=generation,
            role=Role.get_highest_role(club),
            is_current=True,
        )
        return
