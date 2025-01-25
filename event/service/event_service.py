from rest_framework.exceptions import PermissionDenied

from club.models import Generation, GenerationMapping

from ..models import Event
from ..serializers import EventCreateSerializer


class EventService:
    @staticmethod
    def create_event(data: EventCreateSerializer, user):
        generation_id = data.validated_data.get("generation_id")
        # 사용자가 클럽의 관리자인지 확인
        try:
            if not GenerationMapping.objects.get(
                member__user=user, generation__id=generation_id
            ).is_admin():
                raise PermissionDenied("클럽 관리자만 이벤트를 생성할 수 있습니다.")
        except GenerationMapping.DoesNotExist:
            raise PermissionDenied("클럽 관리자만 이벤트를 생성할 수 있습니다.")
        generation = Generation.objects.get(id=generation_id)
        Event.objects.create(
            generation=generation,
            title=data.validated_data.get("title"),
            description=data.validated_data.get("description"),
            location=data.validated_data.get("location"),
            images=data.validated_data.get("images"),
            date=data.validated_data.get("date"),
            start_time=data.validated_data.get("start_time"),
            end_time=data.validated_data.get("end_time"),
            start_minutes=data.validated_data.get("start_minute"),
            late_minutes=data.validated_data.get("late_minute"),
            fail_minutes=data.validated_data.get("fail_minute"),
        )
