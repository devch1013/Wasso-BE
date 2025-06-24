from rest_framework import serializers

from api.userapp.models import User


class UserSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ["id", "username", "email", "phone_number", "profile_image"]


class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "profile_image"]


class UserPushSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["push_allow"]
