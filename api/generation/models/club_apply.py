from django.db import models

from api.generation.models.generation import Generation
from api.userapp.models import User


class ClubApply(models.Model):
    def __str__(self):
        return f"{self.user.username} - {self.generation.name}"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    generation = models.ForeignKey(Generation, on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    accepted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "club_clubapply"
