from .absent_apply import AbsentApplyAdmin
from .abusing import AbusingAdmin
from .attendance import AttendanceAdmin
from .edit_request import EditRequestAdmin
from .event import EventAdmin
from .notice import NoticeAdmin

__all__ = [
    AttendanceAdmin,
    AbsentApplyAdmin,
    EventAdmin,
    NoticeAdmin,
    EditRequestAdmin,
    AbusingAdmin,
]
