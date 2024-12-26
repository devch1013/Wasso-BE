from loguru import logger
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from club import serializers as sz
from club.models import Club, UserClub
from club.services.club_service import ClubService
from main.custom_cache import CacheKey, cache_response, delete_cache_response
from userapp.permissions import IsAuthenticatedCustom


class ClubViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedCustom]

    def get_serializer_class(self):
        if self.action == "create":
            return sz.ClubCreateSerializer
        if self.action == "update":
            return sz.ClubUpdateSerializer
        return sz.ClubInfoSerializer

    @cache_response(timeout=60, key_prefix=CacheKey.CLUB_LIST)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_response(timeout=60, key_prefix=CacheKey.CLUB_DETAIL)
    def retrieve(self, request, *args, **kwargs):
        logger.info(f"Retrieving club detail for user {request.user.id}")
        return super().retrieve(request, *args, **kwargs)

    @delete_cache_response(key_prefix=CacheKey.CLUB_DETAIL)
    def update(self, request, *args, **kwargs):
        instance = Club.objects.get(id=kwargs["pk"])
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def get_queryset(self):
        """사용자가 속한 클럽들을 조회"""
        return UserClub.objects.filter(user=self.request.user).order_by("club__name")

    @delete_cache_response(key_prefix=CacheKey.CLUB_LIST)
    def perform_create(self, serializer: sz.ClubCreateSerializer):
        """클럽 생성"""
        ClubService.create_club(
            user=self.request.user,
            name=serializer.validated_data["name"],
            image_url=serializer.validated_data["image_url"],
            description=serializer.validated_data["description"],
            generation_data=serializer.validated_data["generation"],
        )

    @delete_cache_response(key_prefix=CacheKey.CLUB_LIST)
    @delete_cache_response(key_prefix=CacheKey.CLUB_DETAIL)
    def perform_destroy(self, instance):
        instance.delete()
