from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.userapp.serializers.pc_session_serializers import (
    PcSessionAuthenticationResponseSerializer,
    PcSessionAuthenticationSerializer,
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
                "qrCode": f"wasso://session/{pc_session.code}",
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

    def authenticate(self, request):
        # 인증이 필요한 엔드포인트이므로 인증 확인
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=401)

        # 요청 데이터 검증
        serializer = PcSessionAuthenticationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # 세션 인증 처리
        session = PcSessionService.authenticate_session(
            session_code=data["sessionCode"],
            user=request.user,
            event_id=data["eventId"],
        )

        if session is None:
            return Response({"error": "Invalid session or session expired"}, status=400)

        # 성공 응답
        return Response(PcSessionAuthenticationResponseSerializer(session).data)
