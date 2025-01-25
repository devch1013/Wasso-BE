from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from club.models import GenerationMapping, Member, Role
from club.serializers.member_serializers import (
    MemberDetailSerializer,
    MemberRoleChangeRequestSerializer,
    TagUpdateRequestSerializer,
)


class MemberView(ModelViewSet):
    queryset = GenerationMapping.objects.all()
    serializer_class = MemberDetailSerializer

    def get_serializer(self, *args, **kwargs):
        if self.action == "create":
            return MemberRoleChangeRequestSerializer(*args, **kwargs)
        return super().get_serializer(*args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        queryset = GenerationMapping.objects.get(id=kwargs["pk"])
        serializer = self.get_serializer(queryset)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def role_change(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        requested_role = Role.objects.get(id=serializer.validated_data["role_id"])
        user_generation = GenerationMapping.objects.get(
            id=serializer.validated_data["user_generation_id"]
        )
        user_generation.role = requested_role
        user_generation.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="tags")
    def update_tags(self, request, *args, **kwargs):
        serializer = TagUpdateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_generation = GenerationMapping.objects.get(id=kwargs["pk"])
        user_club = Member.objects.get(
            user=user_generation.member, club=user_generation.generation.club
        )
        user_club.tags = serializer.validated_data["tags"]
        user_club.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def detail(self, request, *args, **kwargs):
        user = request.user
        user_club = Member.objects.get(user=user, club__id=kwargs["pk"])
        serializer = MemberDetailSerializer(user_club)
        return Response(serializer.data, status=status.HTTP_200_OK)
