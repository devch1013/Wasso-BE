from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from club.models import ClubApply, Generation
from club.serializers.club_apply_serializers import ClubApplySerializer


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
