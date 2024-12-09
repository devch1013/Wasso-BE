from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import Event
from ..serializers import EventSerializer

class EventListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """사용자의 upcoming events 조회"""
        club_id = request.query_params.get('clubId')
        
        events = Event.objects.all().filter(club__id=club_id)
            
        serializer = EventSerializer(events, many=True, context={'request': request})
        return Response({"data": serializer.data})