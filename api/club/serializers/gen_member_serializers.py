from rest_framework import serializers

class GenMemberSerializer(serializers.Serializer):
    role_id = serializers.IntegerField()