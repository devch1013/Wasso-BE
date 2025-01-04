from rest_framework.viewsets import GenericViewSet, mixins

from ..serializers.user import UserSerializer


class UserView(
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
