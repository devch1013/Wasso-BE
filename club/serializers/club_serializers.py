from rest_framework import serializers

from club.models import Club, Generation, Position, UserClub, UserGeneration
from club.serializers.generation_serializers import GenerationInfoSerializer


class ClubInfoSerializer(serializers.ModelSerializer):
    club_id = serializers.IntegerField(source="club.id")
    club_name = serializers.CharField(source="club.name")
    club_image_url = serializers.ImageField(
        source="club.image", required=False, allow_null=True
    )
    current_generation = GenerationInfoSerializer(
        source="last_user_generation.generation"
    )
    role = serializers.CharField(source="last_user_generation.role")

    class Meta:
        model = UserClub
        fields = [
            "club_id",
            "club_name",
            "club_image_url",
            "current_generation",
            "role",
        ]

    def get_is_active(self, obj: UserClub):
        return obj.last_user_generation.role != Position.ALUMNI

    def get_start_date(self, obj: UserClub):
        user_generation = (
            UserGeneration.objects.filter(generation__club=obj.club, user=obj.user)
            .order_by("generation__start_date")
            .first()
        )
        return user_generation.generation.start_date if user_generation else None

    def get_end_date(self, obj: UserClub):
        user_generation = (
            UserGeneration.objects.filter(generation__club=obj.club, user=obj.user)
            .order_by("generation__end_date")
            .first()
        )
        return user_generation.generation.end_date if user_generation else None


class ClubUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = ["image_url", "description"]


class UserGenerationSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="club.name")
    image_url = serializers.CharField(source="club.image_url")
    generation_name = serializers.CharField(source="last_generation.name")
    role = serializers.CharField(source="current_role")

    class Meta:
        model = UserClub
        fields = ["id", "name", "image_url", "role", "generation_name"]


class GenerationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Generation
        fields = ["name", "start_date", "end_date"]


class ClubCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    image = serializers.ImageField(required=False, allow_null=True, default=None)
    description = serializers.CharField(max_length=255, required=False, allow_null=True)
    generation = GenerationSerializer()


class ClubGenerationSerializer(serializers.ModelSerializer):
    club_name = serializers.CharField(source="club.name")
    club_image_url = serializers.CharField(source="club.image_url")

    class Meta:
        model = Generation
        fields = ["id", "name", "club_name", "club_image_url"]
