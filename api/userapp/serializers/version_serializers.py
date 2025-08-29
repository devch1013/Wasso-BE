from rest_framework import serializers

from api.userapp.models.user_meta import Platform


class VersionRequestSerializer(serializers.Serializer):
    platform = serializers.ChoiceField(choices=Platform.choices)
    version = serializers.CharField()


class VersionResponseSerializer(serializers.Serializer):
    recent_version = serializers.CharField()
    required = serializers.BooleanField()
