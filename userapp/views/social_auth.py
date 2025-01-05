import requests
from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import User
from ..service.auth import KakaoAuthService, NativeAuthService


class SocialAuthView(
    mixins.CreateModelMixin,
    GenericViewSet,
):
    def create(self, request, *args, **kwargs):
        provider = kwargs.get("provider")
        service = self.get_service(provider)
        if provider == "kakao":
            code = request.query_params.get("code")
            user = service.get_or_create_user(code)
        elif provider == "native":
            identifier = request.data.get("identifier")
            password = request.data.get("password")
            user = service.get_or_create_user(identifier, password)
        refresh = service.get_token(user)
        return Response(
            {
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "token_type": "bearer",
            }
        )

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def _get_kakao_user_info(self, access_token):
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
        }
        response = requests.get("https://kapi.kakao.com/v2/user/me", headers=headers)
        if response.status_code == 200:
            return response.json()
        return None

    def _create_user(self, kakao_token):
        if not kakao_token:
            return Response(
                {"error": "Kakao token is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # 카카오 API로 사용자 정보 가져오기
        user_info = self._get_kakao_user_info(kakao_token)
        if not user_info:
            return Response(
                {"error": "Invalid Kakao token"}, status=status.HTTP_401_UNAUTHORIZED
            )

        # 사용자 생성 또는 조회
        user, _ = User.objects.get_or_create(
            identifier=str(user_info["id"]),
            defaults={
                "username": user_info.get("properties", {}).get("nickname", ""),
            },
        )

        # JWT 토큰 생성
        refresh = RefreshToken.for_user(user)
        return refresh

    def get_service(self, provider: str):
        if provider == "kakao":
            return KakaoAuthService()
        elif provider == "native":
            return NativeAuthService()
        else:
            raise ValueError("Invalid provider")
