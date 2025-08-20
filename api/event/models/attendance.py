from django.db import models

from api.event.models.enums import AttendanceStatus
from api.event.models.event import Event
from api.generation.models import GenMember
from api.userapp.models.user_meta import UniqueToken


class Attendance(models.Model):
    def __str__(self):
        return f"{self.id} - {self.generation_mapping.member.user.username} - {self.event.title} - {AttendanceStatus(self.status).label}"

    generation_mapping = models.ForeignKey(
        GenMember, on_delete=models.CASCADE, related_name="attendances"
    )
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="attendances"
    )
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
    timestamp = models.DateTimeField(auto_now_add=True)  # 삭제예정
    created_at = models.DateTimeField(auto_now_add=True)

    created_by = models.ForeignKey(
        GenMember,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_attendances",
    )
    modified_at = models.DateTimeField(auto_now=True)
    is_modified = models.BooleanField(default=False)

    unique_token = models.ForeignKey(
        UniqueToken,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attendances",
    )

    class Meta:
        db_table = "attendances"
