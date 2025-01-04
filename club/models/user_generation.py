from django.db import models

from userapp.models import User

from .enums import Position
from .generation import Generation


class UserGeneration(models.Model):
    def __str__(self):
        return f"{self.user.username} - {self.generation.club.name} - {self.generation.name} - {self.role}"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    generation = models.ForeignKey(Generation, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    role = models.CharField(
        max_length=10, choices=Position.choices, default=Position.MEMBER
    )

    class Meta:
        db_table = "user_generations"
