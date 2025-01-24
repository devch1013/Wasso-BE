from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from club.models import Role, UserGeneration
from club.serializers.member_serializers import (
    MemberRoleChangeRequestSerializer,
    MemberSerializer,
)


class MemberView(ModelViewSet):
    queryset = UserGeneration.objects.all()
    serializer_class = MemberSerializer

    def get_serializer(self, *args, **kwargs):
        if self.action == "create":
            return MemberRoleChangeRequestSerializer(*args, **kwargs)
        return super().get_serializer(*args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(generation_id=kwargs["pk"])
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def role_change(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        requested_role = Role.objects.get(id=serializer.validated_data["role_id"])
        user_generation = UserGeneration.objects.get(
            id=serializer.validated_data["user_generation_id"]
        )
        user_generation.role = requested_role
        user_generation.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
