from django.db import models


class AttendanceType(models.TextChoices):
    QR = "QR", "QR"
    LOCATION = "LOCATION", "Location"
    BOTH = "BOTH", "Both"


class AttendanceStatus(models.TextChoices):
    PRESENT = "PRESENT", "Present"
    LATE = "LATE", "Late"
    ABSENT = "ABSENT", "Absent"
    FAILED = "FAILED", "Failed"


class AbsentApplyStatus(models.TextChoices):
    PENDING = "PENDING", "대기"
    APPROVED = "APPROVED", "승인"
    REJECTED = "REJECTED", "반려"
