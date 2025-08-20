from api.event.models.edit_request import EditRequest
from api.event.models.event import Event
from api.event.serializers.edit_request_serializer import EditRequestCreateSerializer
from api.event.service.event_service import EventService
from api.generation.models import GenMember
from common.component.fcm_component import FCMComponent
from common.component.notification_template import NotificationTemplate
from common.component.user_selector import UserSelector
from common.exceptions import CustomException, ErrorCode

fcm_component = FCMComponent()


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
            status=serializer.validated_data.get("status"),
            is_approved=False,
        )

        attendance = EventService.change_attendance_status(
            event_id,
            gen_member.id,
            serializer.validated_data.get("status"),
            user,
        )

        notice_users = UserSelector.get_users_by_role(
            generation=event.generation,
            attendance_manage=True,
        )
        fcm_component.send_to_users(
            notice_users,
            NotificationTemplate.EDIT_REQUEST.get_title(
                status=edit_request.get_status_display()
            ),
            NotificationTemplate.EDIT_REQUEST.get_body(
                username=user.username,
                event_name=event.title,
                status=edit_request.get_status_display(),
            ),
            data=NotificationTemplate.EDIT_REQUEST.get_deeplink_data(
                event_id=event.id,
            ),
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
