from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers
from storages.backends.s3boto3 import S3Boto3Storage

from api.club.models import GenMember
from api.club.serializers.member_serializers import MemberSerializer
from api.event.models import Attendance, Event
from api.event.serializers.attend_serializer import AttendanceSerializer


class EventCreateSerializer(serializers.Serializer):
    club_id = serializers.IntegerField()
    generation_id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField(required=False, allow_null=True)
    location = serializers.CharField()
    location_link = serializers.CharField(required=False, allow_null=True)

    images = serializers.ListField(child=serializers.ImageField(), required=False)
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    date = serializers.DateField()
    start_minutes = serializers.IntegerField()
    late_minutes = serializers.IntegerField()
    fail_minutes = serializers.IntegerField()


class EventUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_null=True)
    location = serializers.CharField(required=False, allow_null=True)
    location_link = serializers.CharField(required=False, allow_null=True)
    additional_images = serializers.ListField(
        child=serializers.ImageField(), required=False, allow_null=True
    )
    deleted_images = serializers.ListField(
        child=serializers.CharField(), required=False, allow_null=True
    )
    start_time = serializers.TimeField(required=False, allow_null=True)
    end_time = serializers.TimeField(required=False, allow_null=True)
    date = serializers.DateField(required=False, allow_null=True)
    start_minutes = serializers.IntegerField(required=False, allow_null=True)
    late_minutes = serializers.IntegerField(required=False, allow_null=True)
    fail_minutes = serializers.IntegerField(required=False, allow_null=True)


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
            "location_link",
            "attendance_status",
        ]

    def get_attendance_status(self, obj):
        user = self.context.get("user")
        try:
            attendance = Attendance.objects.filter(
                event=obj, generation_mapping__member__user=user
            ).order_by("-created_at").first()
            
            if attendance is None or attendance.status is None:
                return 0
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
            "location_link",
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
            attendance = Attendance.objects.filter(
                event=obj, generation_mapping__member__user=user
            ).order_by("-created_at").first()
            if attendance is None or attendance.status is None:
                return 0
            return attendance.status
        except Attendance.DoesNotExist:
            return 0


class MemberAttendanceSerializer(serializers.ModelSerializer):
    member_id = serializers.IntegerField(source="member.id")
    member = MemberSerializer()
    attendance_status = serializers.SerializerMethodField()

    class Meta:
        model = GenMember
        fields = ["member_id", "member", "attendance_status"]

    def get_attendance_status(self, obj):
        event = self.context.get("event")
        attendance = Attendance.objects.filter(event=event, generation_mapping=obj).order_by("-created_at").first()
        if attendance:
            return AttendanceSerializer(attendance).data
        return AttendanceSerializer(Attendance(status=0)).data


class EventAttendanceSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ["id", "members"]

    def get_members(self, obj):
        members = obj.generation.genmember_set.all()
        
        # 성(姓)을 기준으로 먼저 정렬하고, 성이 같으면 이름으로 정렬
        members = sorted(members, key=lambda x: (
            x.member.user.username[0],  # 성으로 먼저 정렬
            x.member.user.username[1:]  # 성이 같으면 이름으로 정렬
        ))
        
        return MemberAttendanceSerializer(
            members,
            many=True,
            context={"event": obj},
        ).data
