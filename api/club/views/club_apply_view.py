from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.club.models import ClubApply
from api.club.serializers.club_apply_serializers import (
    ClubApplyApproveSerializer,
    MyClubApplySerializer,
)
from api.club.services.apply_service import ApplyService
from api.userapp.permissions import IsAuthenticatedCustom


class ClubApplyViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedCustom]
    queryset = ClubApply.objects.all()
    serializer_class = MyClubApplySerializer

    def create(self, request, *args, **kwargs):
        club_code = request.query_params.get("club-code")
        ApplyService.apply(request.user, club_code)
        return Response(
            {"message": "Club apply created successfully"},
            status=status.HTTP_201_CREATED,
        )

    def get_queryset(self):
        return ClubApply.objects.filter(user=self.request.user, accepted=False)

    @action(detail=False, methods=["post"])
    def approve(self, request, *args, **kwargs):
        serializer = ClubApplyApproveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        apply_ids = serializer.validated_data["apply_id"]
        club_applies = ApplyService.approve_apply(apply_ids)
        return Response(
            {
                "message": "Club apply approved successfully",
                "club_applies": club_applies.count(),
            },
            status=status.HTTP_200_OK,
        )
