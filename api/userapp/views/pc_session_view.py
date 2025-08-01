from rest_framework.permissions import AllowAny
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
from config.custom_jwt_authentication import CustomJWTAuthentication


class PcSessionView(GenericViewSet):
    permission_classes = [AllowAny]
    authentication_classes = []  # JWT 인증 비활성화

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
        session = PcSessionService.get_session_state(session_id)
        response_data = PcSessionStateResponseSerializer(session)
        # response_data.is_valid()
        return Response(response_data.data)

    def authenticate(self, request):
        # 수동으로 JWT 인증 처리
        jwt_auth = CustomJWTAuthentication()
        try:
            user_auth_tuple = jwt_auth.authenticate(request)
            if user_auth_tuple is None:
                return Response({"error": "Authentication required"}, status=401)

            user, token = user_auth_tuple
            request.user = user
        except Exception:
            return Response({"error": "Authentication required"}, status=401)

        # 요청 데이터 검증
        serializer = PcSessionAuthenticationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # 세션 인증 처리
        session = PcSessionService.authenticate_session(
            session_code=data["sessionCode"],
            user=request.user,
            event_id=1,
        )

        if session is None:
            return Response({"error": "Invalid session or session expired"}, status=400)

        # 성공 응답
        return Response(PcSessionAuthenticationResponseSerializer(session).data)
