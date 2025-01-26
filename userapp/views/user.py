from rest_framework.viewsets import GenericViewSet, mixins

from userapp.serializers.user_serializers import UserSerializer


class UserView(
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    serializer_class = UserSerializer

    def get_object(self):
        print(self.request.user)
        return self.request.user
