from django.db import models


class AttendanceType(models.TextChoices):
    QR = "QR", "QR"
    LOCATION = "LOCATION", "Location"
    BOTH = "BOTH", "Both"


class AttendanceStatus(models.IntegerChoices):
    PRESENT = 1, "출석"
    LATE = 2, "지각"
    ABSENT = 3, "결석"


class AbsentApplyStatus(models.TextChoices):
    PENDING = "PENDING", "대기"
    APPROVED = "APPROVED", "승인"
    REJECTED = "REJECTED", "반려"
