from django.db import models

from .generation import Generation
from .member import Member
from .role import Role


class GenerationMapping(models.Model):
    def __str__(self):
        return f"{self.member.user.username} - {self.generation.club.name} - {self.generation.name} - {self.role}"

    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    generation = models.ForeignKey(Generation, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "generation_mapping"

    def is_admin(self):
        return self.role.event_manage
