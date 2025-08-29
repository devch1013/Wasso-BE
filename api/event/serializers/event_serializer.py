from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers
from storages.backends.s3boto3 import S3Boto3Storage

from api.club.models import GenMember
from api.club.serializers.generation_serializers import SimpleGenerationSerializer
from api.club.serializers.member_serializers import MemberSerializer
from api.event.models import AbsentApply, Attendance, Event
from api.event.models.edit_request import EditRequest
from api.event.serializers.attend_serializer import (
    AbsentApplySerializer,
    AttendanceSerializer,
)
from api.event.serializers.edit_request_serializer import EditRequestSerializer


class EventCreateSerializer(serializers.Serializer):
    club_id = serializers.IntegerField()
    generation_id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField(required=False, allow_null=True)
    location = serializers.CharField()
    location_link = serializers.CharField(required=False, allow_null=True)

    images = serializers.ListField(child=serializers.ImageField(), required=False)
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
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
    start_time = serializers.DateTimeField(required=False, allow_null=True)
    end_time = serializers.DateTimeField(required=False, allow_null=True)
    date = serializers.DateField(required=False, allow_null=True)
    start_minutes = serializers.IntegerField(required=False, allow_null=True)
    late_minutes = serializers.IntegerField(required=False, allow_null=True)
    fail_minutes = serializers.IntegerField(required=False, allow_null=True)


class SimpleEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "date",
            "start_time",
            "end_time",
            "qr_code",
            "location",
        ]


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
            attendance = (
                Attendance.objects.filter(
                    event=obj, generation_mapping__member__user=user
                )
                .order_by("-created_at")
                .first()
            )

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


class EventListForPCSerializer(serializers.ModelSerializer):
    generation = SimpleGenerationSerializer()
    code = serializers.CharField(source="qr_code")

    class Meta:
        model = Event
        fields = [
            "id",
            "code",
            "title",
            "description",
            "date",
            "start_datetime",
            "end_datetime",
            "start_minutes",
            "late_minutes",
            "fail_minutes",
            "location",
            "generation",
        ]


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
            attendance = (
                Attendance.objects.filter(
                    event=obj, generation_mapping__member__user=user
                )
                .order_by("-created_at")
                .first()
            )
            if attendance is None or attendance.status is None:
                return 0
            return attendance.status
        except Attendance.DoesNotExist:
            return 0


class MemberAttendanceSerializer(serializers.ModelSerializer):
    member_id = serializers.IntegerField(source="member.id")
    member = MemberSerializer()
    attendance_status = serializers.SerializerMethodField()
    absent_apply = serializers.SerializerMethodField()
    edit_request = serializers.SerializerMethodField()

    class Meta:
        model = GenMember
        fields = [
            "member_id",
            "member",
            "attendance_status",
            "absent_apply",
            "edit_request",
        ]

    def get_attendance_status(self, obj):
        attendance = self.context.get("attendance_map", {}).get(obj.id)
        if attendance:
            return AttendanceSerializer(attendance).data
        return AttendanceSerializer(Attendance(status=0)).data

    def get_absent_apply(self, obj):
        absent_apply = self.context.get("absent_apply_map", {}).get(obj.id)
        if absent_apply:
            return AbsentApplySerializer(absent_apply).data
        return None

    def get_edit_request(self, obj):
        edit_requests = self.context.get("edit_requests_map", {}).get(obj.id)
        if edit_requests:
            return EditRequestSerializer(edit_requests).data
        return None


class EventAttendanceSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()
    title = serializers.CharField()
    date = serializers.DateField()

    class Meta:
        model = Event
        fields = ["id", "title", "date", "members"]

    def get_members(self, obj):
        # Get all members for this generation
        members = obj.generation.gen_members.all().select_related("member__user")

        # Prefetch all attendance records for this event in a single query
        # Use a dictionary for O(1) lookups instead of filtering in the serializer
        attendances = Attendance.objects.filter(
            event=obj, generation_mapping__in=members
        ).order_by("-created_at")

        # Create a map of gen_member_id -> attendance for efficient lookup
        attendance_map = {}
        for attendance in attendances:
            # Only keep the most recent attendance record for each member
            if attendance.generation_mapping_id not in attendance_map:
                attendance_map[attendance.generation_mapping_id] = attendance

        # Prefetch all absent_apply records for this event in a single query
        absent_applies = AbsentApply.objects.filter(
            event=obj, gen_member__in=members
        ).order_by("created_at")

        edit_requests = EditRequest.objects.filter(
            event=obj, gen_member__in=members
        ).order_by("created_at")

        # Create a map of gen_member_id -> absent_apply for efficient lookup
        absent_apply_map = {
            absent_apply.gen_member_id: absent_apply for absent_apply in absent_applies
        }

        edit_requests_map = {
            edit_request.gen_member_id: edit_request for edit_request in edit_requests
        }

        # Sort members by:
        # 1. First, members with non-approved absent_apply (is_approved=False) come first
        # 2. Then sort by surname and name
        def sort_key(member):
            has_non_approved_absent_apply = False
            if member.id in absent_apply_map:
                has_non_approved_absent_apply = (
                    absent_apply_map[member.id].is_approved is False
                )

            return (
                not has_non_approved_absent_apply,  # False comes first in sorting
                member.member.user.username[0],  # Then sort by surname
                member.member.user.username[1:],  # Then by name
            )

        members = sorted(members, key=sort_key)

        return MemberAttendanceSerializer(
            members,
            many=True,
            context={
                "attendance_map": attendance_map,
                "absent_apply_map": absent_apply_map,
                "edit_requests_map": edit_requests_map,
            },
        ).data


class EventDefaultTimesSerializer(serializers.Serializer):
    start_datetime = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S")
    end_datetime = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S")
    start_minutes = serializers.IntegerField()
    late_minutes = serializers.IntegerField()
    fail_minutes = serializers.IntegerField()
