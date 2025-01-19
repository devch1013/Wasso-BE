from rest_framework import serializers

from event.models import Event


class UpcomingEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["id", "name", "start_datetime", "description"]
