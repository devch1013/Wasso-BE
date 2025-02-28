from rest_framework import serializers

from api.event.models import Attendance


class FloatDecimalField(serializers.DecimalField):
    def to_representation(self, value):
        return round(float(super().to_representation(value)), self.decimal_places)


class CheckQRCodeSerializer(serializers.Serializer):
    qr_code = serializers.CharField()
    latitude = FloatDecimalField(max_digits=10, decimal_places=8, required=False)
    longitude = FloatDecimalField(max_digits=11, decimal_places=8, required=False)


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ["id", "status", "timestamp", "modified_at", "is_modified"]


class ModifyAttendanceSerializer(serializers.Serializer):
    member_id = serializers.IntegerField()
    status = serializers.IntegerField()
