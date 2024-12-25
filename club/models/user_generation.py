from django.db import models
from userapp.models import User
from .generation import Generation
from .enums import Position


class UserGeneration(models.Model):
    def __str__(self):
        return (
            f"{self.user.username} - {self.club.name} - {self.generation} - {self.role}"
        )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    generation = models.ForeignKey(Generation, on_delete=models.CASCADE)
    join_date = models.DateTimeField()
    introduction = models.CharField(max_length=255, null=True, blank=True)
    profile = models.CharField(max_length=255, null=True, blank=True)
    role = models.CharField(
        max_length=10, choices=Position.choices, default=Position.MEMBER
    )

    class Meta:
        db_table = "user_generations"
