from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.userapp.serializers.pc_session_serializers import (
    PcSessionRequestSerializer,
    PcSessionResponseSerializer,
    PcSessionStateResponseSerializer,
)
from api.userapp.service.pc_session_service import PcSessionService


class PcSessionView(GenericViewSet):
    def create(self, request):
        serializer = PcSessionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        pc_session = PcSessionService.create_session(
            platform=data["platform"],
            user_agent=data["userAgent"],
        )

        response_data = PcSessionResponseSerializer(
            data={
                "sessionId": pc_session.code,
                "qrCode": pc_session.code,
                "expiresAt": pc_session.expires_at,
            }
        )
        response_data.is_valid()
        return Response(response_data.data)

    def authenticate_check(self, request, session_id):
        state = PcSessionService.get_session_state(session_id)
        response_data = PcSessionStateResponseSerializer(
            data={
                "sessionCode": session_id,
                "state": state,
                "token": None,
                "userId": None,
                "eventId": None,
            }
        )
        response_data.is_valid()
        return Response(response_data.data)
