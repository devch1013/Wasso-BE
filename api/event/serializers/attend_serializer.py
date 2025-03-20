from rest_framework import serializers

from api.event.models import Attendance


class FloatDecimalField(serializers.DecimalField):
    def to_representation(self, value):
        return round(float(super().to_representation(value)), self.decimal_places)


class CheckQRCodeSerializer(serializers.Serializer):
    qr_code = serializers.CharField()
    latitude = FloatDecimalField(max_digits=11, decimal_places=8, required=False)
    longitude = FloatDecimalField(max_digits=12, decimal_places=8, required=False)
    
    def validate_latitude(self, value):
        if value is not None:
            return round(value, 8)
        return value
    
    def validate_longitude(self, value):
        if value is not None:
            return round(value, 8)
        return value


class AttendanceSerializer(serializers.ModelSerializer):
    timestamp = serializers.DateTimeField(source='created_at', read_only=True)
    class Meta:
        model = Attendance
        fields = ["id", "status", "timestamp", "modified_at", "is_modified"]


class ModifyAttendanceSerializer(serializers.Serializer):
    member_id = serializers.IntegerField()
    status = serializers.IntegerField()

class AttendanceLogSerializer(serializers.Serializer):
    modified = AttendanceSerializer()
    unmodified = AttendanceSerializer()