from rest_framework import serializers
from .models import Club, UserClub

class ClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = ['id', 'name', 'image_url']

class UserClubSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='club.name')
    image_url = serializers.CharField(source='club.image_url')

    class Meta:
        model = UserClub
        fields = ['id', 'name', 'image_url', 'position']