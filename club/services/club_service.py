import random
import string

from django.db import transaction

from club.models import Club, Generation, Position, UserClub, UserGeneration
from main.exceptions import CustomException, ErrorCode
from userapp.models import User


class ClubService:
    @staticmethod
    @transaction.atomic
    def create_club(
        user: User,
        name: str,
        image_url: str,
        description: str,
        generation_data: dict,
    ):
        if Club.objects.filter(name=name).exists():
            raise CustomException(ErrorCode.CLUB_ALREADY_EXISTS)

        club = Club.objects.create(
            name=name,
            image_url=image_url,
            description=description,
        )

        invite_code = "".join(random.choices(string.digits, k=6))

        # 첫 번째 기수(generation) 생성
        generation = Generation.objects.create(
            club=club, **generation_data, invite_code=invite_code
        )

        # 생성자를 owner로 추가
        UserGeneration.objects.create(
            user=user,
            generation=generation,
            role=Position.OWNER.value,
        )

        user_club = UserClub.objects.create(
            user=user,
            club=club,
            last_generation=generation,
            current_role=Position.OWNER.value,
        )

        return club, user_club
