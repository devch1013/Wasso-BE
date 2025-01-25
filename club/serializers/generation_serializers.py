from rest_framework import serializers

from club.models import Generation


class GenerationInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Generation
        fields = "__all__"
