import uuid

from django.db import models

from api.userapp.enums import SessionState


class PcSession(models.Model):
    code = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    platform = models.CharField(max_length=255)
    user_agent = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    state = models.CharField(
        max_length=20,
        choices=SessionState.choices,
        default=SessionState.PENDING,
    )
    user = models.ForeignKey(
        "userapp.User", on_delete=models.CASCADE, null=True, blank=True
    )
    event = models.ForeignKey(
        "event.Event", on_delete=models.CASCADE, null=True, blank=True
    )

    class Meta:
        db_table = "pc_sessions"
