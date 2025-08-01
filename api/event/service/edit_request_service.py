from api.club.models.generation_mapping import GenMember
from api.event.models.edit_request import EditRequest
from api.event.models.event import Event
from api.event.serializers.edit_request_serializer import EditRequestCreateSerializer
from common.exceptions import CustomException, ErrorCode


class EditRequestService:
    @classmethod
    def create_edit_request(
        cls, serializer: EditRequestCreateSerializer, user, event_id
    ):
        event = Event.objects.get(id=event_id)

        gen_member = GenMember.objects.filter(
            member__user=user, generation=event.generation
        ).first()
        if not gen_member:
            raise CustomException(ErrorCode.NOT_REGISTERED_CLUB)

        edit_request = EditRequest.objects.create(
            event=event,
            gen_member=gen_member,
            reason=serializer.validated_data.get("reason"),
            images=serializer.validated_data.get("images"),
        )
        return edit_request

    @classmethod
    def get_edit_requests(cls, event_id, user):
        event = Event.objects.get(id=event_id)
        if (
            GenMember.objects.filter(member__user=user, generation=event.generation)
            .first()
            .is_admin()
        ):
            raise CustomException(ErrorCode.NOT_AUTHORIZED)
        return EditRequest.objects.filter(event=event)
