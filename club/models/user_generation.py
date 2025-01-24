from django.db import models

from userapp.models import User

from .generation import Generation
from .role import Role


class UserGeneration(models.Model):
    def __str__(self):
        return f"{self.user.username} - {self.generation.club.name} - {self.generation.name} - {self.role}"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    generation = models.ForeignKey(Generation, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "user_generations"

    def is_admin(self):
        return self.role.event_manage
