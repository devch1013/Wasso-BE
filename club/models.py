from django.db import models
from userapp.models import User
from enum import Enum

class Club(models.Model):
    def __str__(self):
        return self.name
    
    name = models.CharField(max_length=255)
    president = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clubs_as_president')
    image_url = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'clubs'

class Position(Enum):
    MEMBER = 'MEMBER'
    MANAGER = 'MANAGER'
    ADMIN = 'ADMIN'
    OWNER = 'OWNER'

    @classmethod
    def choices(cls):
        return [(position.value, position.name.capitalize()) for position in cls]

class UserClub(models.Model):
    def __str__(self):
        return f"{self.user.username} - {self.club.name} - {self.generation} - {self.position}"
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    generation = models.CharField(max_length=15)
    join_date = models.DateTimeField()
    introduction = models.CharField(max_length=255, null=True, blank=True)
    profile_picture = models.CharField(max_length=255, null=True, blank=True)
    position = models.CharField(
        max_length=10, 
        choices=Position.choices(), 
        default=Position.MEMBER.value
    )

    class Meta:
        db_table = 'user_clubs'
