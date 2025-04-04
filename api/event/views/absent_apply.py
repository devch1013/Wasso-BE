import logging

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework import status

from ..models import Event, AbsentApply
from ..serializers import AbsentApplySerializer, AbsentApplyCreateSerializer
from api.club.models import GenMember

logger = logging.getLogger(__name__)


class AbsentApplyView(GenericViewSet):
    """
    결석 신청 뷰셋
    """
    permission_classes = [IsAuthenticated]
    lookup_field = "event_id"
    
    def get_queryset(self):
        return AbsentApply.objects.filter(event_id=self.kwargs.get(self.lookup_field))

    def create(self, request, *args, **kwargs):
        """
        결석 신청 생성
        """
        serializer = AbsentApplyCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get event
        event = Event.objects.get(id=kwargs.get(self.lookup_field))
        
        # Get user's gen_member
        gen_member = GenMember.objects.filter(member__user=request.user, generation=event.generation).first()
        
        if not gen_member:
            return Response(
                {"detail": "You are not a member of this generation."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        # Create absent_apply
        absent_apply = AbsentApply.objects.create(
            gen_member=gen_member,
            event=event,
            reason=serializer.validated_data.get("reason"),
            status=serializer.validated_data.get("status"),
            is_approved=False
        )
        
        result = AbsentApplySerializer(absent_apply)
        return Response(result.data, status=status.HTTP_201_CREATED)
