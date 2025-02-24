from rest_framework import serializers

from api.club.models import Generation
from api.club.models import GenerationMapping

class GenerationInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Generation
        fields = "__all__"

class GenerationStatsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField(source="member.user.username")
    present_count = serializers.IntegerField()
    late_count = serializers.IntegerField()
    absent_count = serializers.IntegerField()
    
    class Meta:
        model = GenerationMapping
        fields = ["id", "username", "present_count", "late_count", "absent_count"]

