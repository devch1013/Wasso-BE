from rest_framework import serializers


class PcSessionRequestSerializer(serializers.Serializer):
    platform = serializers.CharField(required=True, help_text="플랫폼 정보")
    userAgent = serializers.CharField(required=True, help_text="사용자 에이전트 정보")


class PcSessionResponseSerializer(serializers.Serializer):
    sessionId = serializers.CharField(required=True, help_text="세션 ID")
    qrCode = serializers.CharField(required=True, help_text="QR 코드")
    expiresAt = serializers.DateTimeField(required=True, help_text="세션 만료 시간")
