from django.db import models
from api.userapp.models import User
from .event import Event
from .enums import AbsentApplyStatus


class AbsentApply(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=AbsentApplyStatus.choices,
        default=AbsentApplyStatus.PENDING.value,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "absent_applies"
