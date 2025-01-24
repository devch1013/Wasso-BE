from rest_framework import serializers

from event.models import Attendance, AttendanceStatus, Event


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


class FloatDecimalField(serializers.DecimalField):
    def to_representation(self, value):
        return float(super().to_representation(value))


class EventDetailSerializer(serializers.ModelSerializer):
    clubId = serializers.IntegerField(source="club_id")
    clubName = serializers.CharField(source="club.name")
    clubImageUrl = serializers.CharField(source="club.image_url")
    eventName = serializers.CharField(source="name")
    eventTime = serializers.DateTimeField(source="start_datetime")
    eventDescription = serializers.CharField(source="description")
    attendanceStartTime = serializers.DateTimeField(source="attendance_start_datetime")
    attendanceEndTime = serializers.DateTimeField(source="attendance_end_datetime")
    hasAttended = serializers.SerializerMethodField()
    latitude = FloatDecimalField(max_digits=10, decimal_places=8)
    longitude = FloatDecimalField(max_digits=11, decimal_places=8)

    class Meta:
        model = Event
        fields = [
            "id",
            "clubId",
            "clubName",
            "clubImageUrl",
            "eventName",
            "eventTime",
            "eventDescription",
            "attendanceStartTime",
            "attendanceEndTime",
            "hasAttended",
            "location",
            "latitude",
            "longitude",
        ]

    def get_hasAttended(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Attendance.objects.filter(
                event=obj, user=request.user, status=AttendanceStatus.PRESENT
            ).exists()
        return False


class CheckQRCodeSerializer(serializers.Serializer):
    qr_code = serializers.CharField()
    latitude = FloatDecimalField(max_digits=10, decimal_places=8)
    longitude = FloatDecimalField(max_digits=11, decimal_places=8)


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["id", "name", "start_datetime", "description"]

    def get_hasAttended(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Attendance.objects.filter(
                event=obj, user=request.user, status=AttendanceStatus.PRESENT
            ).exists()
        return False
