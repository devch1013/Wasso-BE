from django.db import models
from club.models import Club
from decimal import Decimal

class Event(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    attendance_start_datetime = models.DateTimeField()
    attendance_end_datetime = models.DateTimeField()
    late_tolerance_minutes = models.IntegerField()
    location = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    qr_code_url = models.CharField(max_length=255)
    qr_code = models.CharField(max_length=15)

    class Meta:
        db_table = 'events'

class Attendance(models.Model):
    user = models.ForeignKey('userapp.User', on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    attendance_time = models.DateTimeField(auto_now_add=True)
    is_present = models.BooleanField(default=False)
    is_late = models.BooleanField(default=False)

    class Meta:
        db_table = 'attendances'
