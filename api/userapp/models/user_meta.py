from django.db import models

from api.userapp.models.user import User
from config.abstract_models import SoftDeleteModel, TimeStampModel


class FcmToken(SoftDeleteModel, TimeStampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "fcm_tokens"


class UniqueToken(SoftDeleteModel, TimeStampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "unique_tokens"
