from django.db import models
from django.utils import timezone

from api.club.models.generation_mapping import GenMember

from .enums import AttendanceStatus
from .event import Event


class Attendance(models.Model):
    
    def __str__(self):
        return f"{self.generation_mapping.member.user.username} - {self.event.title} - {AttendanceStatus(self.status).label}"
    
    generation_mapping = models.ForeignKey(GenMember, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    status = models.IntegerField(
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.PRESENT,
    )
    latitude = models.DecimalField(
        max_digits=11, decimal_places=8, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=12, decimal_places=8, null=True, blank=True
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_modified = models.BooleanField(default=False)

    class Meta:
        db_table = "attendances"

    def modify_attendance(self, status: int):
        if self.status != status:
            self.status = AttendanceStatus(status)
            self.is_modified = True
            self.modified_at = timezone.localtime(timezone.now())
            self.save()
            return True
        return False
