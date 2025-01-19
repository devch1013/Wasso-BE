from django.db import models

from userapp.models import User

from .enums import AttendanceStatus
from .event import Event


class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    status = models.IntegerField(
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.PRESENT,
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    is_modified = models.BooleanField(default=False)

    class Meta:
        db_table = "attendances"
