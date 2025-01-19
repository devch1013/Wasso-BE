from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Event
from ..serializers import EventDetailSerializer


class EventDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, event_id):
        """특정 이벤트 상세 조회"""
        try:
            event = Event.objects.get(id=event_id)
            serializer = EventDetailSerializer(event, context={"request": request})
            return Response(serializer.data)
        except Event.DoesNotExist:
            return Response(
                {"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND
            )
