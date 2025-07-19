from datetime import datetime, timedelta

from rest_framework.response import Response
from rest_framework.views import APIView

from api.userapp.serializers.pc_session_serializers import (
    PcSessionRequestSerializer,
    PcSessionResponseSerializer,
)


class PcSessionView(APIView):
    def post(self, request):
        serializer = PcSessionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        response_data = PcSessionResponseSerializer(
            data={
                "sessionId": "1234567890",
                "qrCode": "1234567890",
                "expiresAt": datetime.now() + timedelta(minutes=10),
            }
        )
        response_data.is_valid()
        return Response(response_data.data)
