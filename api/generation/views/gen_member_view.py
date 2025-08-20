from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, mixins

from api.club.models import GenMember
from api.generation.serializers.gen_member_serializers import GenMemberSerializer
from api.generation.services import GenMemberService
from common.responses.simple_response import SimpleResponse


class GenMemberView(mixins.DestroyModelMixin, GenericViewSet):
    queryset = GenMember.objects.all()

    @action(detail=True, methods=["put"], url_path="roles")
    def role_change(self, request, *args, **kwargs):
        gen_member = self.get_object()
        serializer = GenMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        GenMemberService.update_gen_member(
            gen_member, serializer.validated_data["role_id"]
        )
        return SimpleResponse("역할 변경 완료")

    def perform_destroy(self, instance):
        GenMemberService.delete_gen_member(instance)

    @action(detail=True, methods=["get"], url_path="attendances")
    def attendances(self, request, *args, **kwargs):
        gen_member = self.get_object()
        attendances = GenMemberService.get_gen_member_attendances(gen_member.id)
        return Response(data=attendances, status=status.HTTP_200_OK)
