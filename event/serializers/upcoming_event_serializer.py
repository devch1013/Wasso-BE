from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from event.models import Attendance, Event


class EventItemSerializer(serializers.ModelSerializer):
    attendance_status = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "date",
            "start_time",
            "end_time",
            "location",
            "attendance_status",
        ]

    def get_attendance_status(self, obj):
        user = self.context.get("user")
        try:
            attendance = Attendance.objects.get(event=obj, user=user)
            return attendance.status
        except Attendance.DoesNotExist:
            return 0


class UpcomingEventSerializer(serializers.Serializer):
    upcoming_events = serializers.SerializerMethodField()
    past_events = serializers.SerializerMethodField()

    def get_past_events(self, obj):
        yesterday = timezone.now().date() - timedelta(days=1)
        print(yesterday)
        past_events = [event for event in self.instance if event.date < yesterday]
        return EventItemSerializer(
            past_events, many=True, context={"user": self.context.get("user")}
        ).data

    def get_upcoming_events(self, obj):
        yesterday = timezone.now().date() - timedelta(days=1)
        upcoming_events = [event for event in self.instance if event.date >= yesterday]
        return EventItemSerializer(
            upcoming_events, many=True, context={"user": self.context.get("user")}
        ).data
