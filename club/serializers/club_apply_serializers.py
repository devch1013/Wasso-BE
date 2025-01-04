from rest_framework import serializers

from club.models import ClubApply


class ClubApplySerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubApply
        fields = "__all__"
