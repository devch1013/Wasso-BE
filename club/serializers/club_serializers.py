from rest_framework import serializers
from club.models import Club, Generation, UserClub, Position, UserGeneration
from django.db import transaction
from django.utils import timezone


class ClubSerializer(serializers.ModelSerializer):
    club_id = serializers.IntegerField(source="club.id")
    club_name = serializers.CharField(source="club.name")
    club_image_url = serializers.CharField(source="club.image_url")
    generation_name = serializers.CharField(source="last_generation.name")
    role = serializers.CharField(source="current_role")

    class Meta:
        model = UserClub
        fields = [
            "id",
            "club_id",
            "club_name",
            "club_image_url",
            "is_active",
            "generation_name",
            "role",
            "start_date",
            "end_date",
        ]

    def get_is_active(self, obj: UserClub):
        return obj.current_role != Position.ALUMNI

    def get_start_date(self, obj: UserClub):
        generation = (
            Generation.objects.filter(club=obj.club, user=obj.user)
            .order_by("start_date")
            .first()
        )
        return generation.start_date if generation else None

    def get_end_date(self, obj: UserClub):
        generation = (
            Generation.objects.filter(club=obj.club, user=obj.user)
            .order_by("end_date")
            .first()
        )
        return generation.end_date if generation else None


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
    image_url = serializers.FileField(required=False)
    description = serializers.CharField(max_length=255, required=False, allow_null=True)
    generation = GenerationSerializer()

    @transaction.atomic
    def create(self, validated_data):
        generation_data = validated_data.pop("generation")

        # 클럽 생성
        club = Club.objects.create(**validated_data)

        # 첫 번째 기수(generation) 생성
        generation = Generation.objects.create(club=club, **generation_data)

        # 생성자를 owner로 추가
        user = self.context["request"].user
        UserGeneration.objects.create(
            user=user,
            generation=generation,
            join_date=timezone.now(),
            role=Position.OWNER.value,
        )

        UserClub.objects.create(
            user=user,
            club=club,
            last_generation=generation,
            current_role=Position.OWNER.value,
        )

        return club
