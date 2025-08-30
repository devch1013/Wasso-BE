from loguru import logger
from rest_framework import serializers

from api.club.models import Club, Generation, GenMember, Member
from api.club.serializers.generation_serializers import (
    GenerationCreateSerializer,
    GenerationInfoSerializer,
)
from api.club.serializers.member_serializers import MemberSerializer
from api.club.serializers.role_serializers import RoleSerializer


## 완료
class ClubInfoSerializer(serializers.Serializer):
    club_id = serializers.IntegerField(source="club.id")
    club_name = serializers.CharField(source="club.name")
    club_image = serializers.ImageField(source="club.image")
    club_description = serializers.CharField(source="club.description")
    generations = serializers.SerializerMethodField()
    current_generation = GenerationInfoSerializer(
        source="get_current_generation.generation", required=False, allow_null=True
    )
    current_member = MemberSerializer(source="*", required=False, allow_null=True)
    is_member_activated: bool = serializers.SerializerMethodField()
    role: RoleSerializer = serializers.SerializerMethodField(
        required=False, allow_null=True
    )
    member_id = serializers.IntegerField(source="id")
    generation_mapping_id = serializers.IntegerField(
        source="get_current_generation.id", required=False, allow_null=True
    )

    class Meta:
        model = Member
        fields = [
            "club_id",
            "club_name",
            "club_image",
            "current_generation",
            "current_member",
            "is_member_activated",
            "role",
            "member_id",
            "generation_mapping_id",
        ]

    def get_is_member_activated(self, obj: Member):
        current_generation = obj.get_current_generation()
        if current_generation:
            return current_generation.generation.activated
        return False

    def get_role(self, obj: Member):
        current_generation = obj.get_current_generation()
        result = RoleSerializer(current_generation.role).data
        return result

    def get_generations(self, obj: Member):
        from api.club.services.generation_service import GenerationService

        generations = GenerationService.get_generations_by_member(obj)
        return GenerationInfoSerializer(generations, many=True).data


class ClubCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    image = serializers.ImageField(required=False, allow_null=True, default=None)
    short_description = serializers.CharField(
        max_length=255, required=False, allow_null=True
    )
    description = serializers.CharField(max_length=255, required=False, allow_null=True)
    generation = GenerationCreateSerializer()


class ClubUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = ["name", "image", "description", "short_description"]

    def update(self, instance, validated_data):
        """클럽 정보 업데이트"""
        instance.name = validated_data.get("name", instance.name)
        instance.image = validated_data.get("image", instance.image)
        instance.description = validated_data.get("description", instance.description)
        instance.short_description = validated_data.get(
            "short_description", instance.short_description
        )
        instance.save()
        return instance


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
