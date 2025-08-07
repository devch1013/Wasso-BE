from rest_framework import serializers

from api.club.models import GenMember, Member
from api.club.serializers.club_serializers import RoleSerializer
from api.club.serializers.generation_serializers import GenerationInfoSerializer
from api.userapp.serializers.user_serializers import UserSerializer


class MemberSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Member
        fields = ["id", "user", "tags", "short_description", "description"]


class GenerationMappingSerializer(serializers.ModelSerializer):
    generation = GenerationInfoSerializer()
    role = RoleSerializer()
    member = MemberSerializer()

    class Meta:
        model = GenMember
        fields = ["id", "generation", "role", "member"]


class MemberRoleChangeRequestSerializer(serializers.Serializer):
    role_id = serializers.IntegerField()
    user_generation_id = serializers.IntegerField()


class TagUpdateRequestSerializer(serializers.Serializer):
    tag = serializers.CharField()


class DescriptionUpdateRequestSerializer(serializers.Serializer):
    description = serializers.CharField(required=False, allow_blank=True)
    short_description = serializers.CharField(required=False, allow_blank=True)


class MemberProfileUpdateRequestSerializer(serializers.Serializer):
    member_id = serializers.IntegerField()
    description = serializers.CharField(required=False, allow_blank=True)
    short_description = serializers.CharField(required=False, allow_blank=True)
    profile_image = serializers.ImageField(required=False)


class MemberDetailSerializer(serializers.ModelSerializer):
    generation = GenerationInfoSerializer()
    role = RoleSerializer()
    user = UserSerializer()
    user_club = serializers.SerializerMethodField()

    def get_user_club(self, obj: GenMember):
        return UserClubSerializer(
            instance=Member.objects.get(user=obj.member, club=obj.generation.club)
        ).data

    class Meta:
        model = GenMember
        fields = ["id", "generation", "role", "user", "user_club"]


class UserClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ["id", "tags", "introduction"]
