from django.db import models

from api.club.models.generation import Generation
from api.club.models.member import Member
from api.club.models.role import Role


class GenMember(models.Model):
    def __str__(self):
        return f"{self.id} - {self.member.user.username}"

    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    generation = models.ForeignKey(
        Generation, on_delete=models.CASCADE, related_name="gen_members"
    )
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
            GenMember.objects.filter(member=self.member, is_current=True).exclude(
                pk=self.pk
            ).update(is_current=False)
        super().save(*args, **kwargs)
