from loguru import logger
from rest_framework import serializers

from club.models import Club, Generation, GenerationMapping, Member
from club.serializers.generation_serializers import GenerationInfoSerializer
from club.serializers.role_serializers import RoleSerializer


## 완료
class ClubInfoSerializer(serializers.Serializer):
    club_id = serializers.IntegerField(source="club.id")
    club_name = serializers.CharField(source="club.name")
    club_image = serializers.ImageField(source="club.image")
    club_description = serializers.CharField(source="club.description")
    current_generation = GenerationInfoSerializer(
        source="last_user_generation.generation"
    )
    is_member_activated = serializers.SerializerMethodField()
    role = RoleSerializer(source="last_user_generation.role")
    member_id = serializers.IntegerField(source="id")
    generation_mapping_id = serializers.IntegerField(source="last_user_generation.id")

    class Meta:
        model = Member
        fields = [
            "club_id",
            "club_name",
            "club_image",
            "current_generation",
            "is_member_activated",
            "role",
            "member_id",
            "generation_mapping_id",
        ]

    def get_is_member_activated(self, obj: Member):
        return obj.last_user_generation.generation == obj.club.current_generation


class ClubCreateSerializer(serializers.Serializer):
    class GenerationSerializer(serializers.ModelSerializer):
        class Meta:
            model = Generation
            fields = ["name", "start_date", "end_date"]

    name = serializers.CharField(max_length=255)
    image = serializers.ImageField(required=False, allow_null=True, default=None)
    description = serializers.CharField(max_length=255, required=False, allow_null=True)
    generation = GenerationSerializer()


class ClubUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = ["image", "description"]


class ClubGenerationSerializer(serializers.ModelSerializer):
    club_name = serializers.CharField(source="club.name")
    club_image = serializers.ImageField(source="club.image")

    class Meta:
        model = Generation
        fields = ["id", "name", "club_name", "club_image"]


class GenerationDetailSerializer(serializers.ModelSerializer):
    invite_code = serializers.IntegerField()

    class Meta:
        model = Generation
        fields = ["id", "name", "invite_code"]


class ClubDetailSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(
        source="image", required=False, allow_null=True
    )
    my_role = serializers.SerializerMethodField()
    current_generation = serializers.SerializerMethodField()
    current_member_count = serializers.SerializerMethodField()

    class Meta:
        model = Club
        fields = [
            "id",
            "name",
            "profile_image",
            "my_role",
            "current_generation",
            "current_member_count",
            "description",
        ]

    def get_my_role(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None

        logger.info(f"request.user: {request.user}")
        logger.info(f"obj: {obj}")
        user_club = Member.objects.get(club=obj, user=request.user)
        if not user_club:
            return None
        return (
            user_club.last_user_generation.role.name
            if user_club.last_user_generation
            else None
        )

    def get_current_generation(self, obj):
        current_gen = obj.current_generation
        if not current_gen:
            return None
        return GenerationDetailSerializer(current_gen).data

    def get_current_member_count(self, obj):
        current_gen = obj.current_generation
        if not current_gen:
            return 0
        return (
            GenerationMapping.objects.filter(generation=current_gen)
            .exclude(role__name="ALUMNI")
            .count()
        )
