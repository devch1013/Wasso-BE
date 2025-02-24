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
    is_current = models.BooleanField(default=True)

    class Meta:
        db_table = "generation_mapping"

    def is_admin(self):
        return self.role.event_manage

    def save(self, *args, **kwargs):
        if self.is_current:
            # 같은 멤버의 다른 GenerationMapping의 is_current를 False로 설정
            GenerationMapping.objects.filter(
                member=self.member, is_current=True
            ).exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)
