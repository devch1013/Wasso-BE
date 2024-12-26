from rest_framework.viewsets import ModelViewSet

from club.models import Club, UserClub
from club.serializers import ClubCreateSerializer, ClubSerializer
from club.services.club_service import ClubService
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
        ClubService.create_club(
            user=self.request.user,
            name=serializer.validated_data["name"],
            image_url=serializer.validated_data["image_url"],
            description=serializer.validated_data["description"],
            generation_data=serializer.validated_data["generation"],
        )
