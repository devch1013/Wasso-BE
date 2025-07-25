from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet, mixins

from api.club.models import GenMember
from api.club.serializers.gen_member_serializers import GenMemberSerializer
from api.club.services.gen_member_service import GenMemberService
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
