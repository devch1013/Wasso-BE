from loguru import logger
from rest_framework import serializers

from api.club.models import Club, Generation, GenMember, Member
from api.club.serializers.generation_serializers import GenerationInfoSerializer, SimpleGenerationSerializer
from api.club.serializers.role_serializers import RoleSerializer


## 완료
class ClubInfoSerializer(serializers.Serializer):
    club_id = serializers.IntegerField(source="club.id")
    club_name = serializers.CharField(source="club.name")
    club_image = serializers.ImageField(source="club.image")
    club_description = serializers.CharField(source="club.description")
    generations = serializers.SerializerMethodField()
    current_generation = GenerationInfoSerializer(
        source="get_current_generation.generation"
    )
    is_member_activated = serializers.SerializerMethodField()
    role = RoleSerializer(source="get_current_generation.role")
    member_id = serializers.IntegerField(source="id")
    generation_mapping_id = serializers.IntegerField(source="get_current_generation.id")

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
        return obj.get_current_generation().generation == obj.club.current_generation
    
    def get_generations(self, obj: Member):
        generations = Generation.objects.filter(club=obj.club, deleted=False)
        return GenerationInfoSerializer(generations, many=True).data


class ClubCreateSerializer(serializers.Serializer):

    name = serializers.CharField(max_length=255)
    image = serializers.ImageField(required=False, allow_null=True, default=None)
    description = serializers.CharField(max_length=255, required=False, allow_null=True)
    generation = SimpleGenerationSerializer()


class ClubUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = ["name", "image", "description"]


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
        member = Member.objects.get(club=obj, user=request.user)
        if not member:
            return None
        return (
            member.get_current_generation().role.name
            if member.get_current_generation()
            else None
        )

    def get_current_generation(self, obj):
        current_gen = obj.current_generation
        if not current_gen:
            return None
        return GenerationInfoSerializer(current_gen).data

    def get_current_member_count(self, obj):
        current_gen = obj.current_generation
        if not current_gen:
            return 0
        return (
            GenMember.objects.filter(generation=current_gen)
            .exclude(role__name="ALUMNI")
            .count()
        )
