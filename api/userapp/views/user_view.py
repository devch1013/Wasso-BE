from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from api.userapp.permissions import IsAuthenticatedCustom
from api.userapp.serializers.user_serializers import UserSerializer, UserPushSerializer
from api.userapp.models import User
from common.component.fcm_component import FCMComponent


class UserView(
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    permission_classes = [IsAuthenticatedCustom]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

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
            "timestamp": "2024-03-21T12:00:00Z"
        }
        
        result = fcm.send_to_user(
            user=user,
            title="테스트 알림",
            body="푸시 알림 테스트입니다.",
            data=test_data
        )
        
        if result:
            return Response({"message": "Push test notification sent successfully"})
        return Response({"message": "Failed to send push test notification"}, status=400)
    
    