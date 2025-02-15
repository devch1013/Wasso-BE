import logging

from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from ..models import Event
from ..serializers import (
    AttendanceSerializer,
    CheckQRCodeSerializer,
    ModifyAttendanceSerializer,
)
from ..service.event_service import EventService

logger = logging.getLogger(__name__)


class EventAttendanceView(GenericViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = CheckQRCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = Event.objects.get(id=serializer.validated_data["event_id"])
        attendance = EventService.check_qr_code(serializer, event, request.user)
        result = AttendanceSerializer(attendance)
        return Response(result.data)

    @action(detail=False, methods=["put"])
    def modify(self, request, *args, **kwargs):
        serializer = ModifyAttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        attendance = EventService.change_attendance_status(
            serializer.validated_data["event_id"],
            serializer.validated_data["member_id"],
            serializer.validated_data["status"],
        )
        result = AttendanceSerializer(attendance)
        return Response(result.data)
