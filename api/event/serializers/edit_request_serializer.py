from rest_framework import serializers

from api.event.models.edit_request import EditRequest


class EditRequestCreateSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True)
    status = serializers.IntegerField()


class EditRequestSerializer(serializers.ModelSerializer):
    approved_by = serializers.CharField(
        source="approved_by.member.user.username", read_only=True
    )

    class Meta:
        model = EditRequest
        fields = [
            "id",
            "reason",
            "status",
            "is_approved",
            "is_rejected",
            "approved_by",
            "created_at",
            "updated_at",
        ]
