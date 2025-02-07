from datetime import timedelta

from django.utils import timezone
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from club.services.club_service import ClubService
from event.models import AttendanceStatus, Event
from userapp.models import User


class EventAttendanceViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="testuser",
            identifier="testuser",
        )

        self.client.force_authenticate(user=self.user)

        self.club, self.member = ClubService.create_club(
            user=self.user,
            name="Test Club",
            description="Test Club Description",
            image=None,
            generation_data={
                "name": "Test Generation",
                "start_date": timezone.now(),
                "end_date": timezone.now() + timedelta(days=1),
            },
        )

        self.event = Event.objects.create(
            generation=self.club.current_generation,
            title="Test Event",
            description="Test Event Description",
            date=timezone.localtime(timezone.now()),
            start_time=timezone.localtime(timezone.now()),
            end_time=timezone.localtime(timezone.now()) + timedelta(days=1),
            start_minutes=0,
            late_minutes=10,
            fail_minutes=30,
            location="Test Location",
            qr_code_url=None,
            qr_code="123456",
        )

    def test_attendance_check(self):
        response = self.client.post(
            reverse("event-attendance-list"),
            data={
                "event_id": self.event.id,
                "qr_code": self.event.qr_code,
                "latitude": 35.123456,
                "longitude": 129.123456,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], AttendanceStatus.PRESENT.value)
