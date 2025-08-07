from api.event.views.absent_apply import AbsentApplyView
from api.event.views.edit_request_view import EditRequestView
from api.event.views.event import EventViewSet
from api.event.views.event_attendance import EventAttendanceView

__all__ = [
    EventViewSet,
    EventAttendanceView,
    AbsentApplyView,
    EditRequestView,
]
