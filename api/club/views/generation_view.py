from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.club.models import ClubApply, Generation, GenerationMapping
from api.club.serializers.club_apply_serializers import ClubApplySerializer
from api.club.serializers.member_serializers import (
    GenerationMappingSerializer,
)
from api.club.serializers.generation_serializers import GenerationStatsSerializer
from api.club.services.generation_service import GenerationService

class GenerationView(ModelViewSet):
    queryset = Generation.objects.all()

    def get_serializer_class(self):
        if self.action == "apply":
            return ClubApplySerializer
        return None

    @action(detail=True, methods=["get"])
    def apply(self, request, *args, **kwargs):
        """Club으로 옮겨야함"""
        applies = ClubApply.objects.filter(generation=self.get_object(), accepted=False)
        serializer = self.get_serializer(applies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def members(self, request, *args, **kwargs):
        """기수별 회원 정보"""
        members = GenerationMapping.objects.filter(generation=self.get_object())
        serializer = GenerationMappingSerializer(members, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def stats(self, request, *args, **kwargs):
        """기수 출석 통계"""
        generation = self.get_object()
        
        # Get all generation mappings and their members
        stats = GenerationService.get_generation_stats(generation.id)
        serializer = GenerationStatsSerializer(stats, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)