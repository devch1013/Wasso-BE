from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.event.serializers.edit_request_serializer import (
    EditRequestCreateSerializer,
    EditRequestSerializer,
)
from api.event.service.edit_request_service import EditRequestService


class EditRequestView(GenericViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = EditRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        edit_request = EditRequestService.create_edit_request(
            serializer, request.user, kwargs.get("event_id")
        )
        return Response(EditRequestSerializer(edit_request).data)

    def list(self, request, *args, **kwargs):
        edit_requests = EditRequestService.get_edit_requests(
            kwargs.get("event_id"), request.user
        )
        return Response(EditRequestSerializer(edit_requests, many=True).data)
