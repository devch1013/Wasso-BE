from django.db import models
from userapp.models import User
from enum import Enum

class Club(models.Model):
    def __str__(self):
        return self.name
    
    name = models.CharField(max_length=255)
    image_url = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    
class Generation(models.Model):
    def __str__(self):
        return f"{self.club.name} - {self.name}"
    
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    done = models.BooleanField(default=False)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)


class UserClub(models.Model):
    def __str__(self):
        return f"{self.user.username} - {self.club.name} - {self.generation} - {self.role}"
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    generation = models.ForeignKey(Generation, on_delete=models.CASCADE)
    join_date = models.DateTimeField()
    introduction = models.CharField(max_length=255, null=True, blank=True)
    profile = models.CharField(max_length=255, null=True, blank=True)
    role = models.CharField(
        max_length=10, 
        choices=Position.choices(), 
        default=Position.MEMBER.value
    )

    class Meta:
        db_table = 'user_clubs'
