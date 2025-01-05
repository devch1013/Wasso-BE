from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from club.models import ClubApply, Generation
from club.models.user_generation import UserGeneration
from club.serializers.club_apply_serializers import (
    ClubApplyApproveSerializer,
    MyClubApplySerializer,
)
from club.services.apply_service import ApplyService
from main.exceptions import CustomException, ErrorCode
from userapp.permissions import IsAuthenticatedCustom


class ClubApplyViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedCustom]
    queryset = ClubApply.objects.all()
    serializer_class = MyClubApplySerializer

    def create(self, request, *args, **kwargs):
        club_code = request.query_params.get("club-code")
        if not club_code:
            raise CustomException(ErrorCode.PARAMS_MISSING)
        generation = Generation.objects.filter(invite_code=club_code).first()
        if not generation:
            raise CustomException(ErrorCode.GENERATION_NOT_FOUND)
        if UserGeneration.objects.filter(
            user=request.user, generation=generation
        ).exists():
            raise CustomException(ErrorCode.ALREADY_APPLIED)
        if ClubApply.objects.filter(user=request.user, generation=generation).exists():
            raise CustomException(ErrorCode.ALREADY_APPLIED)
        ClubApply.objects.create(user=request.user, generation=generation)
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
