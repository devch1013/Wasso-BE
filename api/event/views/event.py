from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, mixins

from api.club.models.member import Member
from api.event.models import Event
from api.event.serializers import (
    EventCreateSerializer,
    EventDetailSerializer,
    EventUpdateSerializer,
    UpcomingEventSerializer,
)
from api.event.serializers.event_serializer import EventListForPCSerializer
from api.event.service.event_service import EventService
from api.generation.serializers.club_apply_serializers import (
    GenerationSimpleInfoSerializer,
)
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
        print("request.data", request.data)
        serializer = EventUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        EventService.update_event(serializer, request.user, kwargs.get("pk"))
        return SimpleResponse("이벤트 수정 완료")

    def generation_info(self, request, *args, **kwargs):
        """
        기수 정보
        /events/{event_id}/generation-info
        """
        generation = EventService.get_generation_info(kwargs.get("event_id"))
        return Response(GenerationSimpleInfoSerializer(generation).data)

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

    @swagger_auto_schema(
        operation_summary="모든 이벤트 정보",
        operation_description="모든 이벤트 정보를 조회합니다.",
        responses={
            200: EventListForPCSerializer(many=True),
            400: "잘못된 요청 데이터",
            401: "인증되지 않은 사용자",
        },
        tags=["푸시 알림"],
    )
    def all_events(self, request, *args, **kwargs):
        """
        모든 이벤트 정보
        """
        member = Member.objects.get(user=request.user)
        events = Event.objects.filter(
            generation__club__id=member.club.id, generation__activated=True
        ).order_by("start_datetime")
        serializer = EventListForPCSerializer(events, many=True)
        return Response(serializer.data)
