from django.db import models

from club.models.generation_mapping import GenerationMapping

from .enums import AttendanceStatus
from .event import Event


class Attendance(models.Model):
    generation_mapping = models.ForeignKey(GenerationMapping, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    status = models.IntegerField(
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.PRESENT,
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_modified = models.BooleanField(default=False)

    class Meta:
        db_table = "attendances"
