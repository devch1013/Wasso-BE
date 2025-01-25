from loguru import logger
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from club import serializers as sz
from club.models import Club, ClubApply, Generation, Member, Role
from club.services.club_service import ClubService
from userapp.permissions import IsAuthenticatedCustom


class ClubViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedCustom]

    def get_serializer_class(self):
        if self.action == "create":
            return sz.ClubCreateSerializer
        if self.action == "update":
            return sz.ClubUpdateSerializer
        if self.action == "retrieve":
            return sz.ClubDetailSerializer
        return sz.ClubInfoSerializer

    # @cache_response(timeout=60, key_prefix=CacheKey.CLUB_LIST)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # @cache_response(timeout=60, key_prefix=CacheKey.CLUB_DETAIL)
    def retrieve(self, request, *args, **kwargs):
        logger.info(f"Retrieving club detail for user {request.user.id}")
        return super().retrieve(request, *args, **kwargs)

    # @delete_cache_response(key_prefix=CacheKey.CLUB_DETAIL)
    def update(self, request, *args, **kwargs):
        instance = Club.objects.get(id=kwargs["pk"])
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def get_queryset(self):
        """사용자가 속한 클럽들을 조회"""
        return Member.objects.filter(user=self.request.user).order_by("club__name")

    def get_object(self):
        return Club.objects.get(id=self.kwargs["pk"])

    # @delete_cache_response(key_prefix=CacheKey.CLUB_LIST)
    def create(self, request, *args, **kwargs):
        # raise CustomException(ErrorCode.NOT_IMPLEMENTED)
        """클럽 생성"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        club, member = ClubService.create_club(
            user=self.request.user,
            name=serializer.validated_data["name"],
            image=serializer.validated_data["image"],
            description=serializer.validated_data["description"],
            generation_data=serializer.validated_data["generation"],
        )

        serializer = sz.ClubInfoSerializer(instance=member)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # @delete_cache_response(key_prefix=CacheKey.CLUB_LIST)
    # @delete_cache_response(key_prefix=CacheKey.CLUB_DETAIL)
    def perform_destroy(self, instance):
        logger.info(f"Deleting club {instance.club.id}")
        instance.club.delete()

    @action(detail=True, methods=["get"])
    def apply(self, request, *args, **kwargs):
        club_apply = ClubApply.objects.filter(generation=kwargs["pk"])
        serializer = sz.ClubApplySerializer(club_apply, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def roles(self, request, *args, **kwargs):
        roles = Role.objects.filter(club__id=kwargs["pk"])
        serializer = sz.RoleSerializer(roles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def generation(self, request, *args, **kwargs):
        generation = Generation.objects.filter(club__id=kwargs["pk"]).order_by(
            "start_date"
        )
        serializer = sz.GenerationInfoSerializer(generation, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
