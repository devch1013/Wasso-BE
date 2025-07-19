from django.db import models


class Provider(models.TextChoices):
    KAKAO = "kakao", "Kakao"
    GOOGLE = "google", "Google"
    APPLE = "apple", "Apple"


class SessionState(models.TextChoices):
    PENDING = "pending", "Pending"
    AUTHENTICATED = "authenticated", "Authenticated"
    USED = "used", "Used"
    EXPIRED = "expired", "Expired"
