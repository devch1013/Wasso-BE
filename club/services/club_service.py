import random
import string

from django.db import transaction

from club.models import Club, Generation, GenerationMapping, Member, Role
from main.exceptions import CustomException, ErrorCode
from userapp.models import User


class ClubService:
    @staticmethod
    @transaction.atomic
    def create_club(
        user: User,
        name: str,
        image,
        description: str,
        generation_data: dict,
    ):
        if Club.objects.filter(name=name).exists():
            raise CustomException(ErrorCode.CLUB_ALREADY_EXISTS)

        club = Club.objects.create(
            name=name,
            image=image,
            description=description,
        )

        invite_code = "".join(random.choices(string.digits, k=6))

        # 첫 번째 기수(generation) 생성
        generation = Generation.objects.create(
            club=club, **generation_data, invite_code=invite_code
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
        user_generation = GenerationMapping.objects.create(
            member=member,
            generation=generation,
            role=owner_role,
        )

        member.last_user_generation = user_generation
        member.save()

        return club, member
