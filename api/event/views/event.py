from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import mixins, GenericViewSet

from ..serializers import (
    EventCreateSerializer,
    EventDetailSerializer,
    EventUpdateSerializer,
    UpcomingEventSerializer,
)

from ..models import Event
from ..service.event_service import EventService
from common.responses.simple_response import SimpleResponse


class EventViewSet(
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return EventCreateSerializer
        elif self.action == "update":
            return EventUpdateSerializer
        return EventDetailSerializer

    def get_object(self):
        return Event.objects.get(id=self.kwargs.get("pk"))

    def get_queryset(self):
        """사용자의 events 조회"""
        club_id = self.request.query_params.get("clubId")
        return Event.objects.filter(generation__club__id=club_id)

    def create(self, request, *args, **kwargs):
        """
        이벤트 생성
        /events/
        """
        serializer = EventCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        EventService.create_event(serializer, request.user)
        return SimpleResponse("이벤트 생성 완료")

    def update(self, request, *args, **kwargs):
        """
        이벤트 수정
        /events/{event_id}/
        """
        serializer = EventUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        EventService.update_event(serializer, request.user, kwargs.get("pk"))
        return SimpleResponse("이벤트 수정 완료")

    @action(detail=False, methods=["get"])
    def upcoming(self, request, *args, **kwargs):
        """
        다가오는 이벤트 정보
        /events/upcoming/?gid={generation_id}
        """
        generation_id = request.query_params.get("gid")
        events = Event.objects.filter(generation__id=generation_id)
        serializer = UpcomingEventSerializer(events, context={"user": request.user})
        return Response(serializer.data)


