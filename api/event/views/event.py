from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

import api.event.serializers as sz

from ..models import Event
from ..serializers import AttendanceSerializer
from ..service.event_service import EventService


class EventViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return sz.EventCreateSerializer
        return sz.EventDetailSerializer

    def get_object(self):
        return Event.objects.get(id=self.kwargs.get("pk"))

    def get_queryset(self):
        """사용자의 events 조회"""
        club_id = self.request.query_params.get("clubId")
        return Event.objects.filter(generation__club__id=club_id)

    def create(self, request, *args, **kwargs):
        """이벤트 생성 시 사용자 권한 확인"""
        serializer = sz.EventCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.request.user
        EventService.create_event(serializer, user)

        return Response({"message": "이벤트 생성 완료"})

    def update(self, request, *args, **kwargs):
        print(request.data)
        serializer = sz.EventUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.request.user
        EventService.update_event(serializer, user, kwargs.get("pk"))

        return Response({"message": "이벤트 수정 완료"})

    @action(detail=False, methods=["get"])
    def upcoming(self, request, *args, **kwargs):
        generation_id = request.query_params.get("gid")
        events = Event.objects.filter(generation__id=generation_id)
        serializer = sz.UpcomingEventSerializer(events, context={"user": request.user})
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def attendance(self, request, *args, **kwargs):
        event = Event.objects.get(id=kwargs.get("pk"))
        serializer = sz.EventAttendanceSerializer(event)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="qr-check")
    def qr_check(self, request, *args, **kwargs):
        print(request.data)
        request.data["latitude"] = round(float(request.data["latitude"]), 8)
        request.data["longitude"] = round(float(request.data["longitude"]), 8)
        serializer = sz.CheckQRCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = Event.objects.get(id=serializer.data.get("event_id"))
        attendance = EventService.check_qr_code(serializer, event, request.user)
        result = AttendanceSerializer(attendance).data
        return Response(result)
