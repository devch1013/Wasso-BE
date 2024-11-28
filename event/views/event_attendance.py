from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from ..models import Event, Attendance

class EventAttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, event_id):
        """이벤트 출석 체크"""
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response(
                {"error": "Event not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        now = timezone.now()
        
        # 출석 가능 시간 체크
        if not (event.attendance_start_datetime <= now <= event.attendance_end_datetime):
            return Response(
                {"error": "Attendance time has expired or not started yet"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 이미 출석했는지 확인
        existing_attendance = Attendance.objects.filter(
            event=event,
            user=request.user
        ).first()

        if existing_attendance:
            return Response(
                {"message": "Already attended"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 지각 여부 확인
        is_late = (now - event.attendance_start_datetime).total_seconds() / 60 > event.late_tolerance_minutes

        # 출석 기록 생성
        Attendance.objects.create(
            user=request.user,
            event=event,
            is_present=True,
            is_late=is_late
        )

        return Response({
            "message": "Attendance recorded successfully",
            "is_late": is_late
        })