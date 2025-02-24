from rest_framework import serializers

from api.club.models import ClubApply
from api.club.serializers.club_serializers import ClubGenerationSerializer
from api.club.serializers.generation_serializers import GenerationInfoSerializer
from api.userapp.serializers import UserSimpleSerializer


class ClubApplySerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer()
    generation = GenerationInfoSerializer()

    class Meta:
        model = ClubApply
        fields = ["id", "user", "created_at", "generation"]


class MyClubApplySerializer(serializers.ModelSerializer):
    generation = ClubGenerationSerializer()

    class Meta:
        model = ClubApply
        fields = ["id", "generation", "created_at"]
