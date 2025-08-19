from django.db import models
from django.utils import timezone

from api.userapp.models.user import User
from config.abstract_models import SoftDeleteModel, TimeStampModel


class FcmToken(SoftDeleteModel, TimeStampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="fcm_tokens")
    token = models.CharField(max_length=255)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "fcm_tokens"


class Platform(models.TextChoices):
    ANDROID = "android"
    IOS = "ios"
    UNKNOWN = "unknown"


class UniqueToken(SoftDeleteModel, TimeStampModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="unique_tokens"
    )
    token = models.CharField(max_length=255)
    model = models.CharField(max_length=255, null=True, blank=True)
    platform = models.CharField(
        max_length=255,
        choices=Platform.choices,
        default=Platform.UNKNOWN,
    )
    active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "unique_tokens"

    def login(self):
        self.last_login = timezone.now()
        self.save()
