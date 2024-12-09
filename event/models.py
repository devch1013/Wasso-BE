from django.db import models
from club.models import Club
from userapp.models import User

class AttendanceType(models.TextChoices):
    QR = 'QR', 'QR'
    LOCATION = 'LOCATION', 'Location' 
    BOTH = 'BOTH', 'Both'

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
        db_table = 'events'

class AttendanceStatus(models.TextChoices):
    PRESENT = 'PRESENT', 'Present'
    LATE = 'LATE', 'Late'
    ABSENT = 'ABSENT', 'Absent'
    FAILED = 'FAILED', 'Failed'
class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=AttendanceStatus.choices, default=AttendanceStatus.PRESENT.value)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_modified = models.BooleanField(default=False)

    class Meta:
        db_table = 'attendances'

class Notice(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notices_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notices'
        

class AbsentApplyStatus(models.TextChoices):
    PENDING = 'PENDING', '대기'
    APPROVED = 'APPROVED', '승인'
    REJECTED = 'REJECTED', '반려'

class AbsentApply(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=AbsentApplyStatus.choices, default=AbsentApplyStatus.PENDING.value)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'absent_applies'
