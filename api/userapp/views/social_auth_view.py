from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.userapp.serializers.user_serializers import (
    MessageResponseSerializer,
    SocialLoginQuerySerializer,
    SocialLoginRequestSerializer,
    TokenSerializer,
)
from api.userapp.service.auth import (
    AppleAuthService,
    GoogleAuthService,
)


class SocialAuthView(
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    """
    소셜 로그인 및 사용자 인증 관련 API 엔드포인트

    Google, Apple 소셜 로그인과 사용자 계정 관리 기능을 제공합니다.
    """

    @swagger_auto_schema(
        operation_summary="소셜 로그인",
        operation_description="""
        소셜 로그인을 통해 사용자 인증을 처리합니다.
        
        지원되는 제공업체:
        - google: Google OAuth 로그인
        - apple: Apple Sign In
        - native: 자체 계정 로그인 (개발용)
        
        성공 시 JWT 토큰을 반환합니다.
        """,
        manual_parameters=[
            openapi.Parameter(
                "provider",
                openapi.IN_PATH,
                description="로그인 제공업체 (google, apple, native)",
                type=openapi.TYPE_STRING,
                required=True,
                enum=["google", "apple", "native"],
            ),
        ],
        query_serializer=SocialLoginQuerySerializer,
        request_body=SocialLoginRequestSerializer,
        responses={
            200: TokenSerializer,
            400: "잘못된 요청 데이터 또는 인증 실패",
            500: "내부 서버 오류",
        },
        tags=["인증"],
    )
    def create(self, request, *args, **kwargs):
        provider = kwargs.get("provider")
        service = self.get_service(provider)

        # 쿼리 파라미터 검증
        query_serializer = SocialLoginQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        query_data = query_serializer.validated_data

        # 요청 바디 검증
        request_serializer = SocialLoginRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        request_data = request_serializer.validated_data

        if provider == "native":
            identifier = request_data.get("identifier")
            password = request_data.get("password")
            user = service.get_or_create_user(identifier, password)
        else:
            code = query_data.get("code")
            fcmToken = query_data.get("fcmToken")
            given_name = request_data.get("given_name")
            family_name = request_data.get("family_name")

            # 이름 조합 로직
            if given_name and family_name:
                name = given_name + " " + family_name
            elif given_name:
                name = given_name
            elif family_name:
                name = family_name
            else:
                name = None
            user = service.get_or_create_user(code, fcmToken, name)

        refresh = service.get_token(user)
        return Response(
            TokenSerializer(
                {
                    "user_id": user.id,
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    "token_type": "bearer",
                }
            ).data
        )

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_service(self, provider: str):
        """인증 서비스 팩토리 메소드"""
        if provider == "google":
            return GoogleAuthService()
        elif provider == "apple":
            return AppleAuthService()
        else:
            raise ValueError("Invalid provider")

    @swagger_auto_schema(
        operation_summary="사용자 계정 탈퇴",
        operation_description="""
        현재 로그인한 사용자의 계정을 완전히 삭제합니다.
        
        Apple 로그인 사용자의 경우 Apple 서버에서도 토큰을 폐기합니다.
        이 작업은 되돌릴 수 없습니다.
        """,
        responses={
            200: MessageResponseSerializer,
            401: "인증되지 않은 사용자",
            500: "내부 서버 오류",
        },
        tags=["사용자 관리"],
    )
    @action(detail=False, methods=["DELETE"], permission_classes=[IsAuthenticated])
    def withdraw(self, request, *args, **kwargs):
        user = request.user
        if user.provider == "apple":
            service = AppleAuthService()
            service.revoke_apple_token(user.identifier)
        user.delete()
        return Response(
            {"message": "User deleted successfully"},
            status=status.HTTP_200_OK,
        )
