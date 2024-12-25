from django.db import transaction
from rest_framework.viewsets import ModelViewSet

from club.models import Club, Generation, Position, UserClub, UserGeneration
from club.serializers import ClubCreateSerializer, ClubSerializer
from userapp.permissions import IsAuthenticatedCustom


class ClubViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedCustom]
    queryset = Club.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return ClubCreateSerializer
        return ClubSerializer

    def get_queryset(self):
        """사용자가 속한 클럽들을 조회"""
        user_clubs = UserClub.objects.filter(user=self.request.user)

        return user_clubs

    def perform_create(self, serializer: ClubCreateSerializer):
        """클럽 생성"""
        with transaction.atomic():
            # 클럽 생성
            # TODO: 서비스로 빼기
            club = Club.objects.create(
                name=serializer.validated_data["name"],
                image_url=serializer.validated_data["image_url"],
                description=serializer.validated_data["description"],
            )

            # 첫 번째 기수(generation) 생성
            generation_data = serializer.validated_data["generation"]
            generation = Generation.objects.create(club=club, **generation_data)

            # 생성자를 owner로 추가
            UserGeneration.objects.create(
                user=self.request.user,
                generation=generation,
                role=Position.OWNER.value,
            )

            UserClub.objects.create(
                user=self.request.user,
                club=club,
                last_generation=generation,
                current_role=Position.OWNER.value,
            )
