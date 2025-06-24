from rest_framework import serializers

from api.club.models import ClubApply
from api.club.serializers.club_serializers import ClubGenerationSerializer
from api.club.serializers.generation_serializers import GenerationInfoSerializer
from api.userapp.models import User


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
