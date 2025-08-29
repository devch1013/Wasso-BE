from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.userapp.models.version import Version
from api.userapp.serializers.version_serializers import (
    VersionRequestSerializer,
    VersionResponseSerializer,
)


class VersionView(GenericAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = VersionRequestSerializer

    def post(self, request):
        print(request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        versions = Version.objects.filter(
            platform=serializer.validated_data.get("platform"),
        ).order_by("-created_at")

        if not versions.exists():
            return Response(
                VersionResponseSerializer(
                    {
                        "recent_version": serializer.validated_data.get("version"),
                        "required": False,
                    }
                ).data
            )

        required_to_update = False

        recent_version = versions.first().version

        for v in versions:
            if v.gt(recent_version):
                recent_version = v.version

            if v.required and v.gt(serializer.validated_data.get("version")):
                required_to_update = True

        return Response(
            VersionResponseSerializer(
                {
                    "recent_version": recent_version,
                    "required": required_to_update,
                }
            ).data
        )
