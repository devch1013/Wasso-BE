from rest_framework import serializers
from event.models import Event, Attendance, AttendanceStatus


class EventCreateSerializer(serializers.ModelSerializer):
    generation = serializers.IntegerField(write_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "start_datetime",
            "end_datetime",
            "generation",
        ]  # 필요한 필드 추가


class FloatDecimalField(serializers.DecimalField):
    def to_representation(self, value):
        return float(super().to_representation(value))


class EventSerializer(serializers.ModelSerializer):
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
