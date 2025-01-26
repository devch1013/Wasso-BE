from rest_framework import serializers

from event.models import Attendance


class FloatDecimalField(serializers.DecimalField):
    def to_representation(self, value):
        return float(super().to_representation(value))


class CheckQRCodeSerializer(serializers.Serializer):
    qr_code = serializers.CharField()
    latitude = FloatDecimalField(max_digits=10, decimal_places=8)
    longitude = FloatDecimalField(max_digits=11, decimal_places=8)


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ["id", "status", "timestamp", "modified_at", "is_modified"]
