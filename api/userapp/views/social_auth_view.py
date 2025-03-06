from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from common.component.fcm_component import FCMComponent

from ..service.auth import (
    AppleAuthService,
    GoogleAuthService,
    KakaoAuthService,
    NativeAuthService,
)


class SocialAuthView(
    mixins.DestroyModelMixin,
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
            fcmToken = request.query_params.get("fcmToken")
            user = service.get_or_create_user(code, fcmToken)

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
        elif provider == "apple":
            return AppleAuthService()
        else:
            raise ValueError("Invalid provider")

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

    @action(detail=False, methods=["post"])
    def send_notification(self, request):
        fcm = FCMComponent()

        fcm.send_notification(
            token="eF9nhyo5SueS-yFehISYOD:APA91bGC3Oo2SnSm51zvX1BZXdvnGHkrozROi-c_iNZ-FXii-FIKkwj3jYbZky_OFrF951zSA443iONBVlh99VWYp8RngNwCmxVWYxfAytuGamZJ47LyROY",
            title="Test Title",
            body="Test Message Body",
            data={"deeplink": "wasso://app/event/checkin/6"},
        )
        return Response({"message": "Notification sent successfully"})
