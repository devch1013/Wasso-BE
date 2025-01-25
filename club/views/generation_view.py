from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from club.models import ClubApply, Generation, GenerationMapping
from club.serializers.club_apply_serializers import ClubApplySerializer
from club.serializers.member_serializers import MemberDetailSerializer, MemberSerializer


class GenerationView(ModelViewSet):
    queryset = Generation.objects.all()

    def get_serializer_class(self):
        if self.action == "apply":
            return ClubApplySerializer
        return None

    @action(detail=True, methods=["get"])
    def apply(self, request, *args, **kwargs):
        applies = ClubApply.objects.filter(generation=self.get_object(), accepted=False)
        serializer = self.get_serializer(applies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def members(self, request, *args, **kwargs):
        members = GenerationMapping.objects.filter(generation=self.get_object())
        serializer = MemberSerializer(members, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def me(self, request, *args, **kwargs):
        user = request.user
        user_generation = GenerationMapping.objects.get(
            user=user, generation=self.get_object()
        )
        serializer = MemberDetailSerializer(user_generation)
        return Response(serializer.data, status=status.HTTP_200_OK)
