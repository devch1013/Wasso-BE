from rest_framework import serializers

from api.event.models import AbsentApply, Attendance


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
    timestamp = serializers.DateTimeField(source="created_at", read_only=True)
    modifier_name = serializers.SerializerMethodField()

    def get_modifier_name(self, obj):
        if obj.created_by:
            return obj.created_by.member.user.username
        return None

    class Meta:
        model = Attendance
        fields = [
            "id",
            "status",
            "timestamp",
            "modified_at",
            "is_modified",
            "modifier_name",
            "created_at",
            "latitude",
            "longitude",
        ]


class ModifyAttendanceSerializer(serializers.Serializer):
    member_id = serializers.IntegerField()
    status = serializers.IntegerField()


class AttendanceLogSerializer(serializers.Serializer):
    modified = AttendanceSerializer()
    unmodified = AttendanceSerializer()


class AbsentApplySerializer(serializers.ModelSerializer):
    approved_by = serializers.CharField(
        source="approved_by.member.user.username", read_only=True
    )

    class Meta:
        model = AbsentApply
        fields = [
            "id",
            "reason",
            "status",
            "is_approved",
            "created_at",
            "updated_at",
            "approved_by",
        ]
        read_only_fields = [
            "id",
            "is_approved",
            "created_at",
            "updated_at",
            "approved_by",
        ]


class AbsentApplyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbsentApply
        fields = ["status", "reason"]
