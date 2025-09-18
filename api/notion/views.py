from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

# Create your views here.


class NotionViewSet(GenericViewSet):
    permission_classes = [AllowAny]
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        print(request.data)
        return Response({"message": "Hello, world!"})
