from django.db import models

from api.club.models import GenMember
from api.event.models.enums import AttendanceStatus
from api.event.models.event import Event


class AbsentApply(models.Model):
    gen_member = models.ForeignKey(GenMember, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.IntegerField(
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.PRESENT,
    )
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        GenMember,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="approved_absent_applies",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "absent_applies"

    def get_status_display(self):
        return AttendanceStatus(self.status).label

    def reject(self, gen_member: GenMember):
        self.is_rejected = True
        self.approved_by = gen_member
        self.save()

    def approve(self, gen_member: GenMember):
        self.is_approved = True
        self.approved_by = gen_member
        self.save()
