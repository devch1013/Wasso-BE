from rest_framework import serializers

from api.event.models.edit_request import EditRequest


class EditRequestCreateSerializer(serializers.Serializer):
    event_id = serializers.IntegerField()
    reason = serializers.CharField()
    images = serializers.ListField(child=serializers.ImageField(), required=False)
    status = serializers.IntegerField(required=False)


class EditRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = EditRequest
        fields = "__all__"
