from django.db import models

from api.event.models.attendance import Attendance


class Abusing(models.Model):
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "abusing"
