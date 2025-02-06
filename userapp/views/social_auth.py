from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from ..service.auth import GoogleAuthService, KakaoAuthService, NativeAuthService


class SocialAuthView(
    mixins.CreateModelMixin,
    GenericViewSet,
):
    def create(self, request, *args, **kwargs):
        provider = kwargs.get("provider")
        service = self.get_service(provider)

        if provider == "native":
            identifier = request.data.get("identifier")
            password = request.data.get("password")
            user = service.get_or_create_user(identifier, password)
        else:
            code = request.query_params.get("code")
            user = service.get_or_create_user(code)

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

    def get_service(self, provider: str):
        if provider == "kakao":
            return KakaoAuthService()
        elif provider == "native":
            return NativeAuthService()
        elif provider == "google":
            return GoogleAuthService()
        else:
            raise ValueError("Invalid provider")
