from rest_framework import serializers


class GenMemberSerializer(serializers.Serializer):
    role_id = serializers.IntegerField()


class AttendanceStatsSerializer(serializers.Serializer):
    total_attendances = serializers.IntegerField()
    total_absences = serializers.IntegerField()
    total_late_attendances = serializers.IntegerField()


class AttendanceSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    status = serializers.IntegerField(read_only=True)
    timestamp = serializers.DateTimeField(source="created_at", read_only=True)
    modifier_name = serializers.SerializerMethodField()
    latitude = serializers.DecimalField(max_digits=11, decimal_places=8, read_only=True)
    longitude = serializers.DecimalField(
        max_digits=12, decimal_places=8, read_only=True
    )


class EventAttendanceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    date = serializers.DateField()
    start_time = serializers.TimeField()
    attendance = AttendanceSerializer(allow_null=True)


class GenMemberAttendanceSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    attendance_stats = AttendanceStatsSerializer()
    events = EventAttendanceSerializer(many=True)
