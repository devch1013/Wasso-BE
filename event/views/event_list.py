from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import Event
from ..serializers import EventSerializer

class EventListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """사용자의 upcoming events 조회"""
        events = Event.objects.all()  # 필요한 필터링 추가 가능
        serializer = EventSerializer(events, many=True, context={'request': request})
        return Response({"data": serializer.data})