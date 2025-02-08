from rest_framework import serializers

from club.models import GenerationMapping, Member
from club.serializers.club_serializers import RoleSerializer
from club.serializers.generation_serializers import GenerationInfoSerializer
from userapp.serializers.user_serializers import UserSerializer


class MemberSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Member
        fields = ["id", "user", "tags", "description"]


class GenerationMappingSerializer(serializers.ModelSerializer):
    generation = GenerationInfoSerializer()
    role = RoleSerializer()
    member = MemberSerializer()

    class Meta:
        model = GenerationMapping
        fields = ["id", "generation", "role", "member"]


class MemberRoleChangeRequestSerializer(serializers.Serializer):
    role_id = serializers.IntegerField()
    user_generation_id = serializers.IntegerField()


class TagUpdateRequestSerializer(serializers.Serializer):
    tag = serializers.CharField()


class DescriptionUpdateRequestSerializer(serializers.Serializer):
    description = serializers.CharField()


class MemberDetailSerializer(serializers.ModelSerializer):
    generation = GenerationInfoSerializer()
    role = RoleSerializer()
    user = UserSerializer()
    user_club = serializers.SerializerMethodField()

    def get_user_club(self, obj: GenerationMapping):
        return UserClubSerializer(
            instance=Member.objects.get(user=obj.member, club=obj.generation.club)
        ).data

    class Meta:
        model = GenerationMapping
        fields = ["id", "generation", "role", "user", "user_club"]


class UserClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ["id", "tags", "introduction"]
