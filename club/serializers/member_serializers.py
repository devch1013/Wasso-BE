from rest_framework import serializers

from club.models import GenerationMapping, Member
from club.serializers.club_serializers import RoleSerializer
from club.serializers.generation_serializers import GenerationInfoSerializer
from userapp.serializers.user_serializers import UserSerializer


class MemberSerializer(serializers.ModelSerializer):
    generation = GenerationInfoSerializer()
    role = RoleSerializer()
    user = UserSerializer()
    tags = serializers.SerializerMethodField()

    def get_tags(self, obj: GenerationMapping):
        user_club = Member.objects.get(user=obj.member, club=obj.generation.club)
        return user_club.tags

    class Meta:
        model = Member
        fields = ["id", "generation", "role", "user", "tags"]


class MemberRoleChangeRequestSerializer(serializers.Serializer):
    role_id = serializers.IntegerField()
    user_generation_id = serializers.IntegerField()


class TagUpdateRequestSerializer(serializers.Serializer):
    tags = serializers.ListField(child=serializers.CharField())


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
