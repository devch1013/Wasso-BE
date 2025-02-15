from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, mixins

from api.userapp.permissions import IsAuthenticatedCustom
from api.userapp.serializers.user_serializers import UserPushSerializer, UserSerializer


class UserView(
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    permission_classes = [IsAuthenticatedCustom]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    @action(detail=False, methods=["POST"])
    def push(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = UserPushSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.push_allow = serializer.validated_data["push_allow"]
        user.save()
        return Response({"message": "Push allow updated successfully"})
