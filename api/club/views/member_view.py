from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.club.models import GenMember, Member, Role
from api.club.serializers.member_serializers import (
    DescriptionUpdateRequestSerializer,
    GenerationMappingSerializer,
    MemberDetailSerializer,
    MemberRoleChangeRequestSerializer,
    TagUpdateRequestSerializer,
)


class MemberView(ModelViewSet):
    queryset = GenMember.objects.all()
    serializer_class = GenerationMappingSerializer

    def get_serializer(self, *args, **kwargs):
        if self.action == "create":
            return MemberRoleChangeRequestSerializer(*args, **kwargs)
        return super().get_serializer(*args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        queryset = GenMember.objects.get(id=kwargs["pk"])
        serializer = self.get_serializer(queryset)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def role_change(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        requested_role = Role.objects.get(id=serializer.validated_data["role_id"])
        user_generation = GenMember.objects.get(
            id=serializer.validated_data["user_generation_id"]
        )
        user_generation.role = requested_role
        user_generation.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["put", "delete"], url_path="tag", url_name="tag")
    def add_tag(self, request, *args, **kwargs):
        if request.method == "PUT":
            serializer = TagUpdateRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            member = Member.objects.get(id=kwargs["pk"])
            member.tags.append(serializer.validated_data["tag"])
            member.save()
        elif request.method == "DELETE":
            serializer = TagUpdateRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            member = Member.objects.get(id=kwargs["pk"])
            member.tags.remove(serializer.validated_data["tag"])
            member.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True, methods=["put"], url_path="description", url_name="description"
    )
    def update_member_profile(self, request, *args, **kwargs):
        serializer = DescriptionUpdateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        member = Member.objects.get(id=kwargs["pk"])
        if serializer.validated_data["description"]:
            member.description = serializer.validated_data["description"]
        if serializer.validated_data["short_description"]:
            member.short_description = serializer.validated_data["short_description"]
        if "profile_image" in serializer.validated_data:
            print(type(serializer.validated_data["profile_image"]))
            member.profile_image = serializer.validated_data["profile_image"]
        member.save()
        result = DescriptionUpdateRequestSerializer(member)
        return Response(result.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def detail(self, request, *args, **kwargs):
        user = request.user
        user_club = Member.objects.get(user=user, club__id=kwargs["pk"])
        serializer = MemberDetailSerializer(user_club)
        return Response(serializer.data, status=status.HTTP_200_OK)
