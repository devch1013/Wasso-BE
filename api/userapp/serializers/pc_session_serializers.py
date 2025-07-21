from rest_framework import serializers

from api.userapp.enums import SessionState
from api.userapp.models.session import PcSession


class PcSessionRequestSerializer(serializers.Serializer):
    platform = serializers.CharField(required=True, help_text="플랫폼 정보")
    userAgent = serializers.CharField(required=True, help_text="사용자 에이전트 정보")


class PcSessionResponseSerializer(serializers.Serializer):
    sessionId = serializers.CharField(required=True, help_text="세션 ID")
    qrCode = serializers.CharField(required=True, help_text="QR 코드")
    expiresAt = serializers.DateTimeField(required=True, help_text="세션 만료 시간")


class PcSessionStateResponseSerializer(serializers.Serializer):
    sessionCode = serializers.CharField(required=True, help_text="세션 코드")
    state = serializers.ChoiceField(
        required=True, choices=SessionState.choices, help_text="세션 상태"
    )
    token = serializers.CharField(required=False, help_text="토큰")
    userId = serializers.IntegerField(required=False, help_text="사용자 ID")
    eventId = serializers.IntegerField(required=False, help_text="이벤트 ID")


class PcSessionAuthenticationSerializer(serializers.Serializer):
    sessionCode = serializers.CharField(required=True, help_text="세션 코드")
    eventId = serializers.IntegerField(required=True, help_text="이벤트 ID")


class PcSessionAuthenticationResponseSerializer(serializers.ModelSerializer):
    code = serializers.CharField(required=True, help_text="세션 코드")
    state = serializers.ChoiceField(
        required=True, choices=SessionState.choices, help_text="세션 상태"
    )

    class Meta:
        model = PcSession
        fields = ["code", "state"]
