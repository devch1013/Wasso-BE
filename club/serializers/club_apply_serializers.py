from rest_framework import serializers

from club.models import ClubApply
from club.serializers.club_serializers import ClubGenerationSerializer
from club.serializers.generation_serializers import GenerationInfoSerializer
from userapp.serializers import UserSimpleSerializer


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


class ClubApplyApproveSerializer(serializers.Serializer):
    apply_id = serializers.ListField(child=serializers.IntegerField())
