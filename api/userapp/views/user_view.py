from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from api.userapp.permissions import IsAuthenticatedCustom
from api.userapp.serializers.user_serializers import UserSerializer, UserPushSerializer
from api.userapp.models import User


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
    
    