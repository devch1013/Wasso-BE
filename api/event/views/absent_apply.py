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
        
    def list(self, request, *args, **kwargs):
        """
        현재 사용자의 특정 이벤트에 대한 가장 최근의 결석 신청 조회
        """
        try:
            # Get event
            event_id = self.kwargs.get(self.lookup_field)
            event = Event.objects.get(id=event_id)
            
            # Get user's gen_member
            gen_member = GenMember.objects.filter(member__user=request.user, generation=event.generation).first()
            
            if not gen_member:
                return Response(
                    {"detail": "You are not a member of this generation."},
                    status=status.HTTP_403_FORBIDDEN
                )
                
            # Get the most recent absent apply for this event and user
            absent_apply = AbsentApply.objects.filter(
                event_id=event_id,
                gen_member=gen_member
            ).order_by('-created_at').first()
            
            if not absent_apply:
                return Response(
                    {"detail": "No absent application found for this event."},
                    status=status.HTTP_404_NOT_FOUND
                )
                
            result = AbsentApplySerializer(absent_apply)
            return Response(result.data, status=status.HTTP_200_OK)
            
        except Event.DoesNotExist:
            return Response(
                {"detail": "Event not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error retrieving absent application: {str(e)}")
            return Response(
                {"detail": "An error occurred while retrieving the absent application."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    def approve(self, request, *args, **kwargs):
        """
        결석 신청 승인
        """
        try:
            # Get the absent apply by its ID from the URL
            absent_apply_id = kwargs.get("pk")
            absent_apply = AbsentApply.objects.get(id=absent_apply_id)
            
            # Approve the absent application
            absent_apply.is_approved = True
            absent_apply.save()
            
            # Return the updated absent application
            result = AbsentApplySerializer(absent_apply)
            return Response(result.data, status=status.HTTP_200_OK)
            
        except AbsentApply.DoesNotExist:
            return Response(
                {"detail": "Absent application not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error approving absent application: {str(e)}")
            return Response(
                {"detail": "An error occurred while approving the absent application."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
