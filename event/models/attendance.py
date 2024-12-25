from django.db import models
from userapp.models import User
from .event import Event
from .enums import AttendanceStatus


class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10,
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.PRESENT.value,
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    is_modified = models.BooleanField(default=False)

    class Meta:
        db_table = "attendances"
