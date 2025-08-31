from django.db import models
from django.utils import timezone

from api.club.models.generation import Generation
from api.userapp.models import User


class ClubApply(models.Model):
    def __str__(self):
        return f"{self.user.username} - {self.generation.name}"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    generation = models.ForeignKey(
        Generation, on_delete=models.CASCADE, related_name="club_applies"
    )
    accepted = models.BooleanField(default=False)
    accepted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def accept(self):
        self.accepted = True
        self.accepted_at = timezone.now()
        self.save()
