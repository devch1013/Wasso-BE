from rest_framework import status
from rest_framework.viewsets import GenericViewSet

from api.club.services.apply_service import ApplyService
from api.userapp.permissions import IsAuthenticatedCustom
from common.responses.simple_response import SimpleResponse
from common.exceptions import CustomException, ErrorCode

class ClubApplyViewSet(GenericViewSet):
    permission_classes = [IsAuthenticatedCustom]

    def apply(self, request, *args, **kwargs):
        club_code = request.query_params.get("club-code")
        if not club_code:
            raise CustomException(ErrorCode.PARAMS_MISSING)
        ApplyService.apply(request.user, club_code)
        return SimpleResponse(
            "Club apply created successfully",
            status=status.HTTP_201_CREATED,
        )
        
    def approve(self, request, *args, **kwargs):
        apply_id = kwargs.get("apply_id")
        ApplyService.approve_apply(apply_id)
        return SimpleResponse(
            "Club apply approved successfully",
            status=status.HTTP_200_OK,
        )

    def reject(self, request, *args, **kwargs):
        apply_id = kwargs.get("apply_id")
        ApplyService.reject_apply(apply_id)
        return SimpleResponse(
            "Club apply rejected successfully",
            status=status.HTTP_200_OK,
        )
