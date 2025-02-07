import logging

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from ..models import Event
from ..serializers import AttendanceSerializer, CheckQRCodeSerializer
from ..service.event_service import EventService

logger = logging.getLogger(__name__)


class EventAttendanceView(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = CheckQRCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = Event.objects.get(id=serializer.validated_data["event_id"])
        attendance = EventService.check_qr_code(serializer, event, request.user)
        result = AttendanceSerializer(attendance)
        return Response(result.data)
