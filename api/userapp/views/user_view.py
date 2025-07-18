from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.userapp.models import User
from api.userapp.permissions import IsAuthenticatedCustom
from api.userapp.serializers.user_serializers import (
    MessageResponseSerializer,
    PushSettingResponseSerializer,
    PushTestResponseSerializer,
    UserPushSerializer,
    UserSerializer,
)
from common.component.fcm_component import FCMComponent


class UserView(
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    """
    사용자 관련 API 엔드포인트

    현재 로그인한 사용자의 정보를 조회하고 수정할 수 있습니다.
    """

    permission_classes = [IsAuthenticatedCustom]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    @swagger_auto_schema(
        operation_summary="현재 사용자 정보 조회",
        operation_description="JWT 토큰을 통해 인증된 현재 사용자의 정보를 조회합니다.",
        responses={
            200: UserSerializer,
            401: "인증되지 않은 사용자",
        },
        tags=["사용자"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="현재 사용자 정보 수정",
        operation_description="JWT 토큰을 통해 인증된 현재 사용자의 정보를 수정합니다.",
        request_body=UserSerializer,
        responses={
            200: UserSerializer,
            400: "잘못된 요청 데이터",
            401: "인증되지 않은 사용자",
        },
        tags=["사용자"],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        methods=["post"],
        operation_summary="푸시 알림 설정 변경",
        operation_description="사용자의 푸시 알림 허용 여부를 설정합니다.",
        request_body=UserPushSerializer,
        responses={
            200: MessageResponseSerializer,
            400: "잘못된 요청 데이터",
            401: "인증되지 않은 사용자",
        },
        tags=["푸시 알림"],
    )
    @swagger_auto_schema(
        methods=["get"],
        operation_summary="푸시 알림 설정 조회",
        operation_description="현재 사용자의 푸시 알림 허용 여부를 조회합니다.",
        responses={
            200: PushSettingResponseSerializer,
            401: "인증되지 않은 사용자",
        },
        tags=["푸시 알림"],
    )
    @action(detail=False, methods=["POST", "GET"])
    def push(self, request, *args, **kwargs):
        """푸시 알림 설정"""
        user: User = self.get_object()
        if request.method == "POST":
            serializer = UserPushSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user.push_allow = serializer.validated_data["push_allow"]
            user.save()
            return Response({"message": "Push allow updated successfully"})
        if request.method == "GET":
            return Response({"push_allow": user.push_allow})

    @swagger_auto_schema(
        operation_summary="푸시 알림 테스트",
        operation_description="현재 사용자에게 테스트 푸시 알림을 발송합니다. 개발 및 테스트 목적으로 사용됩니다.",
        responses={
            200: PushTestResponseSerializer,
            400: PushTestResponseSerializer,
            401: "인증되지 않은 사용자",
        },
        tags=["푸시 알림"],
    )
    @action(detail=False, methods=["POST"])
    def push_test(self, request, *args, **kwargs):
        """푸시 테스트"""
        user: User = self.get_object()
        fcm = FCMComponent()

        # 테스트용 데이터
        test_data = {
            "deeplink": "wasso://event/checkin?id=16",
            "type": "test",
            "message": "This is a test push notification",
            "timestamp": "2024-03-21T12:00:00Z",
        }

        result = fcm.send_to_user(
            user=user,
            title="테스트 알림",
            body="푸시 알림 테스트입니다.",
            data=test_data,
        )

        if result:
            return Response({"message": "Push test notification sent successfully"})
        return Response(
            {"message": "Failed to send push test notification"}, status=400
        )
