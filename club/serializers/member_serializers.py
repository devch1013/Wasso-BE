from rest_framework import serializers

from club.models import Role, UserGeneration
from club.serializers.generation_serializers import GenerationInfoSerializer
from userapp.serializers.user_serializers import UserSerializer


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name"]


class MemberSerializer(serializers.ModelSerializer):
    generation = GenerationInfoSerializer()
    role = RoleSerializer()
    user = UserSerializer()

    class Meta:
        model = UserGeneration
        fields = ["id", "generation", "role", "user"]


class MemberRoleChangeRequestSerializer(serializers.Serializer):
    role_id = serializers.IntegerField()
    user_generation_id = serializers.IntegerField()
