from rest_framework import serializers

from api.club.models import Generation, GenMember


class SimpleGenerationSerializer(serializers.ModelSerializer):
    club_name = serializers.CharField(source="club.name")
    club_image = serializers.ImageField(source="club.image")

    class Meta:
        model = Generation
        fields = ["id", "name", "start_date", "end_date", "club_name", "club_image"]


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
        model = GenMember
        fields = ["id", "username", "present_count", "late_count", "absent_count"]


class NotionIdSerializer(serializers.Serializer):
    notion_database_url = serializers.CharField(required=False, allow_null=True)
