from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers
from storages.backends.s3boto3 import S3Boto3Storage

from club.models import GenerationMapping
from club.serializers.member_serializers import MemberSerializer
from event.models import Attendance, Event
from event.serializers.attend_serializer import AttendanceSerializer


class EventCreateSerializer(serializers.Serializer):
    club_id = serializers.IntegerField()
    generation_id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField(required=False, allow_null=True)
    location = serializers.CharField()

    images = serializers.ListField(child=serializers.ImageField(), required=False)
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    date = serializers.DateField()
    start_minute = serializers.IntegerField()
    late_minute = serializers.IntegerField()
    fail_minute = serializers.IntegerField()


class EventSerializer(serializers.ModelSerializer):
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
            attendance = Attendance.objects.get(
                event=obj, generation_mapping__member__user=user
            )
            return attendance.status
        except Attendance.DoesNotExist:
            return 0


class UpcomingEventSerializer(serializers.Serializer):
    upcoming_events = serializers.SerializerMethodField()
    past_events = serializers.SerializerMethodField()

    def get_past_events(self, obj):
        yesterday = timezone.now().date() - timedelta(days=1)
        past_events = [event for event in self.instance if event.date < yesterday]
        return EventSerializer(
            past_events, many=True, context={"user": self.context.get("user")}
        ).data

    def get_upcoming_events(self, obj):
        yesterday = timezone.now().date() - timedelta(days=1)
        upcoming_events = [event for event in self.instance if event.date >= yesterday]
        return EventSerializer(
            upcoming_events, many=True, context={"user": self.context.get("user")}
        ).data


class EventDetailSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    attendance_status = serializers.SerializerMethodField()
    qr_code_url = serializers.ImageField()

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
            "start_minutes",
            "late_minutes",
            "fail_minutes",
            "images",
            "qr_code_url",
            "qr_code",
            "attendance_status",
        ]

    def get_images(self, obj):
        if not obj.images:
            return []
        storage = S3Boto3Storage()
        return [storage.url(image_path) for image_path in obj.images]

    def get_attendance_status(self, obj):
        user = self.context.get("request").user
        try:
            attendance = Attendance.objects.get(
                event=obj, generation_mapping__member__user=user
            )
            return attendance.status
        except Attendance.DoesNotExist:
            return 0


class MemberAttendanceSerializer(serializers.ModelSerializer):
    member = MemberSerializer()
    attendance_status = serializers.SerializerMethodField()

    class Meta:
        model = GenerationMapping
        fields = ["id", "member", "attendance_status"]

    def get_attendance_status(self, obj):
        event = self.context.get("event")
        try:
            attendance = Attendance.objects.get(event=event, generation_mapping=obj)
            return AttendanceSerializer(attendance).data
        except Attendance.DoesNotExist:
            return AttendanceSerializer(Attendance(status=0)).data


class EventAttendanceSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ["id", "members"]

    def get_members(self, obj):
        return MemberAttendanceSerializer(
            obj.generation.generationmapping_set.all(),
            many=True,
            context={"event": obj},
        ).data
