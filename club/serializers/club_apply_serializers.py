from rest_framework import serializers

from club.models import ClubApply
from userapp.serializers.user import UserSimpleSerializer


class ClubApplySerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer()

    class Meta:
        model = ClubApply
        fields = ["id", "user", "created_at"]
