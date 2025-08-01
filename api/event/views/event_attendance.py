import logging

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.event.models import Attendance, Event
from api.event.serializers import (
    AttendanceLogSerializer,
    AttendanceSerializer,
    CheckQRCodeSerializer,
    EventAttendanceSerializer,
    ModifyAttendanceSerializer,
)
from api.event.service.event_service import EventService
from common.responses.simple_response import SimpleResponse

logger = logging.getLogger(__name__)


class EventAttendanceView(
    GenericViewSet,
):
    permission_classes = [IsAuthenticated]
    lookup_field = "event_id"

    def get_queryset(self):
        return Attendance.objects.filter(event_id=self.kwargs.get(self.lookup_field))

    def create(self, request, *args, **kwargs):
        request.data["latitude"] = round(float(request.data["latitude"]), 8)
        request.data["longitude"] = round(float(request.data["longitude"]), 8)
        serializer = CheckQRCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = Event.objects.get(id=kwargs.get(self.lookup_field))
        attendance = EventService.check_qr_code(serializer, event, request.user)
        result = AttendanceSerializer(attendance)
        return Response(result.data)

    def modify(self, request, *args, **kwargs):
        serializer = ModifyAttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        attendance = EventService.change_attendance_status(
            kwargs.get(self.lookup_field),
            serializer.validated_data["member_id"],
            serializer.validated_data["status"],
            request.user,
        )
        result = AttendanceSerializer(attendance)
        return Response(result.data)

    def attendances(self, request, *args, **kwargs):
        """이벤트 출석 정보 조회"""
        event = Event.objects.get(id=kwargs.get(self.lookup_field))
        serializer = EventAttendanceSerializer(event)
        return Response(serializer.data)

    def qr_check(self, request, *args, **kwargs):
        request.data["latitude"] = round(float(request.data["latitude"]), 8)
        request.data["longitude"] = round(float(request.data["longitude"]), 8)
        serializer = CheckQRCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = Event.objects.get(id=kwargs.get("pk"))
        attendance = EventService.check_qr_code(serializer, event, request.user)
        return Response(AttendanceSerializer(attendance).data)

    def attendance_all(self, request, *args, **kwargs):
        event = Event.objects.get(id=kwargs.get(self.lookup_field))
        EventService.attend_all(event, request.user)
        return SimpleResponse(message="출석 처리 완료")

    def me(self, request, *args, **kwargs):
        event = Event.objects.get(id=kwargs.get(self.lookup_field))
        attendance = EventService.get_me(event, request.user)
        return Response(AttendanceSerializer(attendance).data)

    def get_member_log(self, request, *args, **kwargs):
        """멤버 출석 로그 조회"""

        event = Event.objects.get(id=kwargs.get(self.lookup_field))
        gen_member_id = kwargs.get("gen_member_id")
        attendance = EventService.get_member_log(event, gen_member_id)
        print(attendance)
        return Response(AttendanceLogSerializer(attendance).data)
