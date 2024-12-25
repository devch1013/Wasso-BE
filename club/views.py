from rest_framework.views import APIView
from rest_framework.response import Response
from userapp.permissions import IsAuthenticatedCustom
from .models import Club, UserGeneration, Generation, Position, UserClub
from .serializers import UserGenerationSerializer, ClubCreateSerializer
from django.db import transaction
from django.utils import timezone
from rest_framework import status

# Create your views here.


class ClubListView(APIView):
    permission_classes = [IsAuthenticatedCustom]

    def get(self, request):
        """사용자가 속한 클럽들을 조회"""
        user_clubs = UserClub.objects.filter(user=request.user)

        serializer = UserGenerationSerializer(user_clubs, many=True)
        print(serializer.data)
        return Response({"data": serializer.data})

    def post(self, request):
        """클럽 생성"""
        serializer = ClubCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 트랜잭션으로 처리
        with transaction.atomic():
            # 클럽 생성
            club = Club.objects.create(
                name=serializer.validated_data["name"],
                image_url=serializer.validated_data.get("image_url"),
                description=serializer.validated_data.get("description"),
            )

            # 첫 번째 기수(generation) 생성
            generation_data = serializer.validated_data["generation"]
            generation = Generation.objects.create(club=club, **generation_data)

            # 생성자를 owner로 추가
            UserGeneration.objects.create(
                user=request.user,
                generation=generation,
                join_date=timezone.now(),
                role=Position.OWNER.value,
            )

            UserClub.objects.create(
                user=request.user,
                club=club,
                last_generation=generation,
                current_role=Position.OWNER.value,
            )

        return Response(
            {
                "message": "Club created successfully",
                "data": {"id": club.id, "name": club.name},
            },
            status=status.HTTP_201_CREATED,
        )
