from rest_framework import serializers
from .models import Club, UserGeneration, Generation, UserClub

class ClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = ['id', 'name', 'image_url']

class UserGenerationSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='club.name')
    image_url = serializers.CharField(source='club.image_url')
    generation_name = serializers.CharField(source='last_generation.name')
    role = serializers.CharField(source='current_role')
    class Meta:
        model = UserClub
        fields = ['id', 'name', 'image_url', 'role', 'generation_name']

class GenerationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Generation
        fields = ['name', 'start_date', 'end_date']

class ClubCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    image_url = serializers.CharField(max_length=255, required=False, allow_null=True)
    description = serializers.CharField(max_length=255, required=False, allow_null=True)
    generation = GenerationSerializer()