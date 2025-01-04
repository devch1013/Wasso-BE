from rest_framework import serializers

from ..models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "phone_number", "profile_image"]


class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "profile_image"]
