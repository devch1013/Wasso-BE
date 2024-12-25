from django.db import models
from userapp.models import User
from .club import Club
from .generation import Generation
from .enums import Position


class UserClub(models.Model):
    def __str__(self):
        return f"{self.user.username} - {self.club.name} - {self.role}"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    current_role = models.CharField(
        max_length=10, choices=Position.choices, default=Position.MEMBER
    )
    last_generation = models.ForeignKey(Generation, on_delete=models.CASCADE)

    class Meta:
        db_table = "user_clubs"
