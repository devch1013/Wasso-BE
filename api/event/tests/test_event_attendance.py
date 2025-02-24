from datetime import timedelta

from django.utils import timezone
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase
from unittest.mock import patch
from common.test_utils.image_utils import ImageTestUtils

from api.club.services.club_service import ClubService, GenerationMapping
from api.event.models import Attendance, AttendanceStatus, Event
from api.userapp.models import User


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

        self.event: Event = Event.objects.create(
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

    @patch("django.core.files.storage.default_storage.save")
    def test_attendance_check(self, mock_storage):
        """정상 출석 체크"""
        mock_storage.return_value = "test-image-path.jpg"

        now = timezone.localtime(timezone.now())
        end_time = (now + timedelta(hours=1)).time()

        event = Event.objects.create(
            title="Test Event",
            description="Test Event Description",
            location="Test Location",
            images=[ImageTestUtils.create_test_image()],
            generation=self.club.current_generation,
            date=now.date(),
            start_time=now.time(),
            end_time=end_time,
            start_minutes=-10,
            late_minutes=10,
            fail_minutes=30,
            qr_code="123456",
            qr_code_url=None,
        )

        response = self.client.post(
            reverse("event-attendance", kwargs={"event_id": event.id}),
            data={
                "event_id": event.id,
                "qr_code": event.qr_code,
                "latitude": 35.123456,
                "longitude": 129.123456,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], AttendanceStatus.PRESENT.value)

    def test_attendance_modify(self):
        """apply 기록 없을 때 변경"""
        response = self.client.put(
            reverse("event-attendance", kwargs={"event_id": self.event.id}),
            data={
                "event_id": self.event.id,
                "member_id": self.member.id,
                "status": AttendanceStatus.LATE.value,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], AttendanceStatus.LATE.value)
        self.assertEqual(response.data["is_modified"], True)

    def test_attendance_modify_with_apply(self):
        """apply 기록 있을 때 변경"""
        generation_mapping = GenerationMapping.objects.get(
            member=self.member, generation=self.event.generation
        )
        attendance = Attendance.objects.create(
            event=self.event,
            generation_mapping=generation_mapping,
            status=AttendanceStatus.PRESENT,
        )

        self.assertEqual(attendance.status, AttendanceStatus.PRESENT.value)
        self.assertEqual(attendance.is_modified, False)
        response = self.client.put(
            reverse("event-attendance", kwargs={"event_id": self.event.id}),
            data={
                "event_id": self.event.id,
                "member_id": self.member.id,
                "status": AttendanceStatus.LATE.value,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], AttendanceStatus.LATE.value)
        self.assertEqual(response.data["is_modified"], True)

        attendance.refresh_from_db()
        self.assertEqual(attendance.status, AttendanceStatus.LATE.value)
        self.assertEqual(attendance.is_modified, True)
