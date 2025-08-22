from loguru import logger
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.club.models import Club, Member, Role
from api.club.serializers import (
    ClubCreateSerializer,
    ClubDetailSerializer,
    ClubInfoSerializer,
    ClubUpdateSerializer,
    RoleSerializer,
)
from api.club.services.club_service import ClubService
from api.generation.models import ClubApply, Generation
from api.generation.serializers.club_apply_serializers import ClubApplySerializer
from api.generation.serializers.generation_serializers import (
    GenerationCreateSerializer,
    GenerationInfoSerializer,
)
from api.userapp.permissions import IsAuthenticatedCustom


class ClubView(ModelViewSet):
    permission_classes = [IsAuthenticatedCustom]

    def get_queryset(self):
        return Member.objects.filter(
            user=self.request.user, club__deleted=False
        ).order_by("club__name")

    def get_object(self):
        return Club.objects.get(id=self.kwargs["pk"], deleted=False)

    def get_serializer_class(self):
        if self.action == "create":
            return ClubCreateSerializer
        if self.action == "update":
            return ClubUpdateSerializer
        if self.action == "retrieve":
            return ClubDetailSerializer
        return ClubInfoSerializer

    # @cache_response(timeout=60, key_prefix=CacheKey.CLUB_LIST)
    def list(self, request, *args, **kwargs):
        """
        [GET] /clubs/
        사용자가 속한 클럽들을 조회
        """
        return super().list(request, *args, **kwargs)

    # @cache_response(timeout=60, key_prefix=CacheKey.CLUB_DETAIL)
    def retrieve(self, request, *args, **kwargs):
        """
        [GET] /clubs/{pk}/
        클럽 상세 조회
        """
        return super().retrieve(request, *args, **kwargs)

    # @delete_cache_response(key_prefix=CacheKey.CLUB_DETAIL)
    def update(self, request, *args, **kwargs):
        """
        [PUT] /clubs/{pk}/
        동아리 정보 수정
        """
        return super().update(request, *args, **kwargs)

    # @delete_cache_response(key_prefix=CacheKey.CLUB_LIST)
    def create(self, request, *args, **kwargs):
        # raise CustomException(ErrorCode.NOT_IMPLEMENTED)
        """클럽 생성"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        print("serializer", serializer.validated_data)

        club, member = ClubService.create_club(
            user=self.request.user,
            name=serializer.validated_data["name"],
            image=serializer.validated_data["image"],
            description=serializer.validated_data["description"],
            generation_data=serializer.validated_data["generation"],
        )

        serializer = ClubInfoSerializer(instance=member)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # @delete_cache_response(key_prefix=CacheKey.CLUB_LIST)
    # @delete_cache_response(key_prefix=CacheKey.CLUB_DETAIL)
    def perform_destroy(self, instance):
        logger.info(f"Deleting club {instance.name}")
        instance.delete()

    @action(detail=True, methods=["get"])
    def applies(self, request, *args, **kwargs):
        """클럽 가입 신청 목록 조회"""
        club_apply = ClubApply.objects.filter(generation=kwargs["pk"])
        serializer = ClubApplySerializer(club_apply, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def roles(self, request, *args, **kwargs):
        """클럽 역할 목록 조회"""
        roles = Role.objects.filter(club__id=kwargs["pk"])
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get", "post"])
    def generations(self, request, *args, **kwargs):
        """클럽 기수 목록 조회"""
        if request.method == "POST":
            serializer = GenerationCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            ClubService.create_generation(
                club=self.get_object(),
                generation_data=serializer.validated_data,
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == "GET":
            generation = Generation.objects.filter(
                club__id=kwargs["pk"], deleted=False, club__deleted=False
            ).order_by("start_date")
            serializer = GenerationInfoSerializer(generation, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
