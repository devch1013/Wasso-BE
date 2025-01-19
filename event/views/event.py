from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

import event.serializers as sz
from club.models import Generation, UserGeneration

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

    def create(self, request, *args, **kwargs):
        """이벤트 생성 시 사용자 권한 확인"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        generation_id = request.data.get("generation_id")
        user = self.request.user
        # 사용자가 클럽의 관리자인지 확인
        try:
            if not UserGeneration.objects.get(
                user=user, generation__id=generation_id
            ).is_admin():
                raise PermissionDenied("클럽 관리자만 이벤트를 생성할 수 있습니다.")
        except UserGeneration.DoesNotExist:
            raise PermissionDenied("클럽 관리자만 이벤트를 생성할 수 있습니다.")
        generation = Generation.objects.get(id=generation_id)
        Event.objects.create(
            generation=generation,
            title=serializer.validated_data.get("title"),
            description=serializer.validated_data.get("description"),
            location=serializer.validated_data.get("location"),
            images=serializer.validated_data.get("images"),
            date=serializer.validated_data.get("date"),
            start_datetime=serializer.validated_data.get("start_time"),
            end_datetime=serializer.validated_data.get("end_time"),
            start_minutes=serializer.validated_data.get("start_minute"),
            late_minutes=serializer.validated_data.get("late_minute"),
            fail_minutes=serializer.validated_data.get("fail_minute"),
        )
        return Response({"message": "이벤트 생성 완료"})

    @action(detail=False, methods=["get"])
    def upcoming(self, request, *args, **kwargs):
        generation_id = request.query_params.get("gid")
        events = Event.objects.filter(generation__id=generation_id)
        serializer = sz.UpcomingEventSerializer(events)
        return Response(serializer.data)
