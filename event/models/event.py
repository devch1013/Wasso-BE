from django.db import models
from club.models import Club
from .enums import AttendanceType


class Event(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    attendance_start_datetime = models.DateTimeField()
    attendance_end_datetime = models.DateTimeField()
    begin_minutes = models.IntegerField()
    late_tolerance_minutes = models.IntegerField()
    location = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    qr_code_url = models.CharField(max_length=255)
    qr_code = models.CharField(max_length=15)
    attendance_type = models.CharField(max_length=10, choices=AttendanceType.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "events"
