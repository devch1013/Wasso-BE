from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import math
import logging
from ..models import Event, Attendance
from ..serializers import CheckQRCodeSerializer
from django.utils import timezone

logger = logging.getLogger(__name__)

class EventQRCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, event_id):
        """QR 코드 체크 및 출석 체크"""
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            logger.warning(f"Event not found - event_id: {event_id}, user: {request.user}")
            return Response(
                {"error": "Event not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # QR 코드 및 위치 확인
        serializer = CheckQRCodeSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Invalid QR code data - event_id: {event_id}, user: {request.user}, errors: {serializer.errors}")
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if event.qr_code != serializer.validated_data['qr_code']:
            logger.warning(f"Invalid QR code - event_id: {event_id}, user: {request.user}")
            return Response(
                {"code": 1, "message": "잘못된 QR코드입니다"},
                status=status.HTTP_400_BAD_REQUEST
            )

        distance = self.calculate_distance(event, serializer)
        if distance > 5:
            logger.warning(f"User too far from event location - event_id: {event_id}, user: {request.user}, distance: {distance}m")
            return Response(
                {"code": 2, "message": "인증 위치와 너무 떨어져있습니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 출석 체크 로직
        now = timezone.localtime(timezone.now())
        
        if not (event.attendance_start_datetime <= now <= event.attendance_end_datetime):
            logger.warning(f"Attendance time expired - event_id: {event_id}, user: {request.user}, current_time: {now}")
            return Response(
                {"code": 3, "message": "출석 가능한 시간이 아닙니다"},
                status=status.HTTP_400_BAD_REQUEST
            )

        existing_attendance = Attendance.objects.filter(
            event=event,
            user=request.user
        ).first()

        if existing_attendance:
            logger.warning(f"Duplicate attendance - event_id: {event_id}, user: {request.user}")
            return Response(
                {"code": 4, "message": "이미 출석하였습니다"},
                status=status.HTTP_400_BAD_REQUEST
            )

        is_late = (now - event.attendance_start_datetime).total_seconds() / 60 > event.late_tolerance_minutes

        Attendance.objects.create(
            user=request.user,
            event=event,
            is_present=True,
            is_late=is_late
        )

        return Response({
            "status": "success",
            "code": 0,
            "message": "출석 완료",
            "is_late": is_late
        })

    def calculate_distance(self, event, serializer):
        R = 6371000  # 지구의 반지름 (미터)
        lat1, lon1 = float(event.latitude), float(event.longitude)
        lat2, lon2 = float(serializer.validated_data['latitude']), float(serializer.validated_data['longitude'])

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2) * math.sin(delta_phi / 2) + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) * math.sin(delta_lambda / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        return distance