from django.db import models

from userapp.models import User

from .club import Club
from .enums import Position
from .user_generation import UserGeneration


class UserClub(models.Model):
    def __str__(self):
        return f"{self.user.username} - {self.club.name} - {self.current_role}"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="user_clubs")
    current_role = models.CharField(
        max_length=10, choices=Position.choices, default=Position.MEMBER
    )
    last_user_generation = models.ForeignKey(UserGeneration, on_delete=models.CASCADE)
    introduction = models.TextField(null=True, blank=True)
    profile_image_url = models.ImageField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_clubs"
