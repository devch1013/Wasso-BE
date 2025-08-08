from rest_framework import serializers

from api.club.models import ClubApply
from api.club.models.generation import Generation
from api.club.serializers.club_serializers import ClubGenerationSerializer
from api.club.serializers.generation_serializers import GenerationInfoSerializer
from api.userapp.models import User


class GenerationSimpleInfoSerializer(serializers.ModelSerializer):
    club_name = serializers.CharField(source="club.name")
    generation_name = serializers.CharField(source="name")
    club_description = serializers.CharField(source="club.description")
    club_image = serializers.ImageField(source="club.image")
    auto_approve = serializers.BooleanField()
    invite_code = serializers.CharField()
    member_count = serializers.IntegerField()

    class Meta:
        model = Generation
        fields = [
            "generation_name",
            "club_name",
            "club_description",
            "club_image",
            "auto_approve",
            "invite_code",
            "member_count",
        ]


class UserApplySimpleSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["username", "profile_image", "email"]

    def get_username(self, obj):
        if obj.username:
            return obj.username
        else:
            return "익명"


class ClubApplySerializer(serializers.ModelSerializer):
    user = UserApplySimpleSerializer()
    generation = GenerationInfoSerializer()

    class Meta:
        model = ClubApply
        fields = ["id", "user", "created_at", "generation"]


class MyClubApplySerializer(serializers.ModelSerializer):
    generation = ClubGenerationSerializer()

    class Meta:
        model = ClubApply
        fields = ["id", "generation", "created_at"]
