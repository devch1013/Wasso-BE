from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.generation.models import ClubApply, Generation
from api.generation.serializers.club_apply_serializers import (
    GenerationSimpleInfoSerializer,
    MyClubApplySerializer,
)
from api.generation.services import ApplyService
from api.userapp.permissions import IsAuthenticatedCustom
from common.component.fcm_component import FCMComponent
from common.component.user_selector import UserSelector
from common.exceptions import CustomException, ErrorCode
from common.responses.simple_response import SimpleResponse


class ApplyView(mixins.ListModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticatedCustom]
    serializer_class = MyClubApplySerializer

    def get_queryset(self):
        return ClubApply.objects.filter(user=self.request.user, accepted=False)

    @action(detail=False, methods=["get"], url_path="info", url_name="club-apply-info")
    def get_info(self, request):
        club_code = request.query_params.get("code")
        if not club_code:
            raise CustomException(ErrorCode.PARAMS_MISSING)
        generation = ApplyService.get_generation_from_code(club_code)
        return Response(
            GenerationSimpleInfoSerializer(generation).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="", url_name="club-apply")
    def apply(self, request, *args, **kwargs):
        club_code = request.query_params.get("club-code")
        if not club_code:
            raise CustomException(ErrorCode.PARAMS_MISSING)
        ApplyService.apply(request.user, club_code)
        return SimpleResponse(
            "Club apply created successfully",
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="", url_name="club-apply-approve")
    def approve(self, request, *args, **kwargs):
        apply_id = kwargs.get("apply_id")
        ApplyService.approve_apply(apply_id)
        return SimpleResponse(
            "Club apply approved successfully",
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["delete"], url_path="", url_name="club-apply-reject")
    def reject(self, request, *args, **kwargs):
        apply_id = kwargs.get("apply_id")
        ApplyService.reject_apply(apply_id)
        return SimpleResponse(
            "Club apply rejected successfully",
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="notice-test",
        url_name="club-apply-notice-test",
    )
    def notice_test(self, request, *args, **kwargs):
        users = UserSelector.get_users_by_role(
            generation=Generation.objects.get(invite_code="760267"),
            signup_accept=True,
        )
        fcm_component = FCMComponent()
        fcm_component.send_to_users(users, "test", "test")
        return SimpleResponse("success", status=status.HTTP_200_OK)
