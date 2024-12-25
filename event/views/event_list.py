from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from ..models import Event
from ..serializers import EventSerializer


class EventViewSet(ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """사용자의 events 조회"""
        club_id = self.request.query_params.get("clubId")
        return Event.objects.filter(club__id=club_id)

    def perform_create(self, serializer):
        """이벤트 생성 시 사용자 권한 확인"""
        club_id = self.request.data.get("club")
        user = self.request.user

        # 사용자가 클럽의 관리자인지 확인
        if not user.clubs.filter(id=club_id, clubmember__is_admin=True).exists():
            raise PermissionDenied("클럽 관리자만 이벤트를 생성할 수 있습니다.")

        serializer.save()
