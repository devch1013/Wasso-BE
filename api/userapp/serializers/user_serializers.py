from rest_framework import serializers

from api.userapp.models import User
from api.userapp.models.user_meta import Platform


class UserSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "phone_number",
            "profile_image",
            "initialized",
        ]


class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "profile_image"]


class UserPushSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["push_allow"]


class TokenSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    access_token = serializers.CharField(required=True)
    refresh_token = serializers.CharField(required=True)
    token_type = serializers.CharField(required=True)


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(required=True)


# 소셜 로그인용 Serializer들
class SocialLoginRequestSerializer(serializers.Serializer):
    """소셜 로그인 요청 데이터"""

    given_name = serializers.CharField(
        required=False, help_text="사용자 이름 (소셜 로그인)"
    )
    family_name = serializers.CharField(
        required=False, help_text="사용자 성 (소셜 로그인)"
    )
    identifier = serializers.CharField(
        required=False, help_text="사용자 ID (native 로그인)"
    )
    password = serializers.CharField(
        required=False, write_only=True, help_text="비밀번호 (native 로그인)"
    )
    fcm_token = serializers.CharField(
        required=False, help_text="FCM 토큰 (푸시 알림용)"
    )
    device_id = serializers.CharField(required=False, help_text="Device ID")
    platform = serializers.ChoiceField(
        required=False,
        choices=Platform.choices,
        default=Platform.UNKNOWN,
    )
    model = serializers.CharField(required=False, help_text="Device Model")


class SocialLoginQuerySerializer(serializers.Serializer):
    """소셜 로그인 쿼리 파라미터"""

    code = serializers.CharField(
        required=False, help_text="OAuth 인증 코드 (소셜 로그인 시 필요)"
    )
    fcmToken = serializers.CharField(required=False, help_text="FCM 토큰 (푸시 알림용)")


class PushTestResponseSerializer(serializers.Serializer):
    """푸시 테스트 응답 데이터"""

    message = serializers.CharField(help_text="응답 메시지")


class PushSettingResponseSerializer(serializers.Serializer):
    """푸시 설정 응답 데이터"""

    push_allow = serializers.BooleanField(help_text="푸시 알림 허용 여부")


class MessageResponseSerializer(serializers.Serializer):
    """일반적인 메시지 응답"""

    message = serializers.CharField(help_text="응답 메시지")
