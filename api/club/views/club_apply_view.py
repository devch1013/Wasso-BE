from rest_framework import status
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from api.club.services.apply_service import ApplyService
from api.userapp.permissions import IsAuthenticatedCustom
from common.responses.simple_response import SimpleResponse
from common.exceptions import CustomException, ErrorCode
from api.club.serializers.club_apply_serializers import MyClubApplySerializer
from api.club.models import ClubApply

from common.component.fcm_component import FCMComponent
from common.component.user_selector import UserSelector
from api.club.models import Generation

class ClubApplyViewSet(mixins.ListModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticatedCustom]
    serializer_class = MyClubApplySerializer

    def get_queryset(self):
        return ClubApply.objects.filter(user=self.request.user, accepted=False)

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
        
    def notice_test(self, request, *args, **kwargs):
        users = UserSelector.get_users_by_role(
            generation=Generation.objects.get(invite_code="760267"),
            signup_accept=True,
        )
        fcm_component = FCMComponent()
        fcm_component.send_to_users(users, "test", "test")
        return SimpleResponse("success", status=status.HTTP_200_OK)
