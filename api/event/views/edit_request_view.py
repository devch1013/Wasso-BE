from loguru import logger
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.event.models.edit_request import EditRequest
from api.event.models.event import Event
from api.event.serializers.edit_request_serializer import (
    EditRequestCreateSerializer,
    EditRequestSerializer,
)
from api.event.service.edit_request_service import EditRequestService
from api.generation.models import GenMember
from common.component.fcm_component import FCMComponent
from common.component.notification_template import NotificationTemplate


class EditRequestView(GenericViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        print(request.data)
        serializer = EditRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        edit_request = EditRequestService.create_edit_request(
            serializer, request.user, kwargs.get("event_id")
        )

        return Response(EditRequestSerializer(edit_request).data)

    def list(self, request, *args, **kwargs):
        try:
            # Get event
            event_id = kwargs.get("event_id")
            event = Event.objects.get(id=event_id)

            # Get user's gen_member
            gen_member = GenMember.objects.filter(
                member__user=request.user, generation=event.generation
            ).first()

            if not gen_member:
                return Response(
                    {"detail": "You are not a member of this generation."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Get the most recent absent apply for this event and user
            edit_request = (
                EditRequest.objects.filter(event_id=event_id, gen_member=gen_member)
                .order_by("-created_at")
                .first()
            )

            if not edit_request:
                return Response(
                    {"detail": "No absent application found for this event."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            result = EditRequestSerializer(edit_request)

            return Response(result.data, status=status.HTTP_200_OK)

        except Event.DoesNotExist:
            logger.error(f"Event not found: {event_id}")
            return Response(
                {"detail": "Event not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error retrieving absent application: {str(e)}")
            return Response(
                {
                    "detail": "An error occurred while retrieving the absent application."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def approve(self, request, *args, **kwargs):
        """
        결석 신청 승인
        """
        fcm_component = FCMComponent()
        try:
            # Get the absent apply by its ID from the URL
            absent_apply_id = kwargs.get("pk")
            absent_apply = EditRequest.objects.get(id=absent_apply_id)
            approve_gen_member = GenMember.objects.get(
                member__user=request.user, generation=absent_apply.event.generation
            )

            # Approve the absent application
            absent_apply.is_approved = True
            absent_apply.approved_by = approve_gen_member
            absent_apply.save()

            # Return the updated absent application
            result = EditRequestSerializer(absent_apply)
            fcm_component.send_to_user(
                absent_apply.gen_member.member.user,
                NotificationTemplate.EDIT_REQUEST_APPROVE.get_title(
                    status=absent_apply.get_status_display()
                ),
                NotificationTemplate.EDIT_REQUEST_APPROVE.get_body(
                    event_name=absent_apply.event.title,
                    status=absent_apply.get_status_display(),
                ),
                data=NotificationTemplate.EDIT_REQUEST_APPROVE.get_deeplink_data(
                    event_id=absent_apply.event.id,
                ),
            )
            return Response(result.data, status=status.HTTP_200_OK)

        except EditRequest.DoesNotExist:
            return Response(
                {"detail": "Absent application not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error approving absent application: {str(e)}")
            return Response(
                {"detail": "An error occurred while approving the absent application."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
