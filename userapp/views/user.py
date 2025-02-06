from rest_framework.viewsets import GenericViewSet, mixins

from userapp.permissions import IsAuthenticatedCustom
from userapp.serializers.user_serializers import UserSerializer


class UserView(
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    permission_classes = [IsAuthenticatedCustom]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
