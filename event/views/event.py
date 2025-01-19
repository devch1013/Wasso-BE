from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

import event.serializers as sz

from ..models import Event


class EventViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return sz.EventCreateSerializer
        return sz.EventDetailSerializer

    def get_queryset(self):
        """사용자의 events 조회"""
        club_id = self.request.query_params.get("clubId")
        return Event.objects.filter(generation__club__id=club_id)

    def perform_create(self, serializer: serializers.ModelSerializer):
        """이벤트 생성 시 사용자 권한 확인"""
        generation_id = serializer.validated_data.get("generation")
        user = self.request.user

        # 사용자가 클럽의 관리자인지 확인
        if not user.generations.filter(
            id=generation_id, usergeneration__is_admin=True
        ).exists():
            raise PermissionDenied("클럽 관리자만 이벤트를 생성할 수 있습니다.")

        serializer.save()
