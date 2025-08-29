from datetime import timedelta
from unittest.mock import patch

from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase

from api.club.services.club_service import ClubService
from api.event.models import Event
from api.userapp.models import User
from common.test_utils.image_utils import ImageTestUtils


class EventViewSetTests(APITestCase):
    @patch("django.core.files.storage.default_storage.save")
    def setUp(self, mock_storage):
        mock_storage.return_value = "test-image-path.jpg"
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

    def test_get_event(self):
        """이벤트 조회"""
        now = timezone.now()
        event = Event.objects.create(
            title="Test Event",
            description="Test Event Description",
            location="Test Location",
            images=[],
            generation=self.club.current_generation,
            date=now.date(),
            start_time=now.time(),
            end_time=(now + timedelta(hours=1)).time(),
            start_minutes=0,
            late_minutes=10,
            fail_minutes=30,
        )

        response = self.client.get(reverse("event-detail", kwargs={"pk": event.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Test Event")
        self.assertEqual(response.data["description"], "Test Event Description")
        self.assertEqual(response.data["location"], "Test Location")
        self.assertEqual(len(response.data["images"]), 0)
        self.assertEqual(response.data["attendance_status"], 0)

    @patch("django.core.files.storage.default_storage.save")
    def test_create_event(self, mock_storage):
        """이벤트 생성"""
        mock_storage.return_value = "test-image-path.jpg"
        data = {
            "club_id": self.club.id,
            "generation_id": self.club.current_generation.id,
            "title": "Test Event",
            "description": "Test Event Description",
            "location": "Test Location",
            "images": [
                ImageTestUtils.create_test_image(),
            ],
            "date": "2018-01-01",
            "start_time": "10:00",
            "end_time": "11:00",
            "start_minutes": 0,
            "late_minutes": 10,
            "fail_minutes": 30,
        }
        response = self.client.post(reverse("event-list"), data, format="multipart")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Event.objects.first().title, "Test Event")
        self.assertEqual(Event.objects.first().description, "Test Event Description")
        self.assertEqual(Event.objects.first().location, "Test Location")
        self.assertEqual(len(Event.objects.first().images), 1)

    def upcoming_event(self):
        """다가오는 이벤트 조회"""
        Event.objects.create(
            title="Test Event",
            description="Test Event Description",
            location="Test Location",
            images=[],
            generation=self.club.current_generation,
            date=timezone.now().date() + timedelta(days=1),
            start_time=timezone.now().time() + timedelta(hours=1),
            end_time=timezone.now().time() + timedelta(hours=2),
            start_minutes=0,
            late_minutes=10,
            fail_minutes=30,
        )

        response = self.client.get(
            reverse("event-upcoming", kwargs={"gid": self.club.current_generation.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Test Event")

    @patch("django.core.files.storage.default_storage.save")
    def test_update_event(self, mock_storage):
        """이벤트 수정"""
        mock_storage.return_value = "test-image-path.jpg"

        event = Event.objects.create(
            title="Test Event",
            description="Test Event Description",
            location="Test Location",
            images=[ImageTestUtils.create_test_image()],
            generation=self.club.current_generation,
            date="2018-01-01",
            start_time="10:00",
            end_time="11:00",
            start_minutes=0,
            late_minutes=10,
            fail_minutes=30,
        )

        data = {
            "title": "Updated Event",
            "description": "Updated Event Description",
            "location": "Updated Location",
            "additional_images": [
                ImageTestUtils.create_test_image(),
                ImageTestUtils.create_test_image(),
            ],
            "deleted_images": [
                "https://wasso.com/" + event.images[0],
            ],
        }
        response = self.client.put(
            reverse("event-detail", kwargs={"pk": event.id}), data, format="multipart"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Event.objects.first().title, "Updated Event")
        self.assertEqual(Event.objects.first().description, "Updated Event Description")
        self.assertEqual(Event.objects.first().location, "Updated Location")
        self.assertEqual(len(Event.objects.first().images), 2)

    def test_delete_event(self):
        """이벤트 삭제"""
        event1 = Event.objects.create(
            title="Test Event1",
            description="Test Event Description",
            location="Test Location",
            images=[],
            generation=self.club.current_generation,
            date="2018-01-01",
            start_time="10:00",
            end_time="11:00",
            start_minutes=0,
            late_minutes=10,
            fail_minutes=30,
        )
        event2 = Event.objects.create(
            title="Test Event2",
            description="Test Event Description",
            location="Test Location",
            images=[],
            generation=self.club.current_generation,
            date="2018-01-01",
            start_time="10:00",
            end_time="11:00",
            start_minutes=0,
            late_minutes=10,
            fail_minutes=30,
        )
        self.assertEqual(Event.objects.count(), 2)
        response = self.client.delete(reverse("event-detail", kwargs={"pk": event1.id}))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Event.objects.first().id, event2.id)

    def test_get_event_default_times(self):
        """이벤트 기본 시간 조회"""

        Event.objects.create(
            title="Test Event1",
            description="Test Event Description",
            location="Test Location",
            images=[],
            generation=self.club.current_generation,
            date="2018-01-01",
            start_datetime="2018-01-01T10:00:00",
            end_datetime="2018-01-01T11:00:00",
            start_minutes=0,
            late_minutes=10,
            fail_minutes=30,
        )
        response = self.client.get(
            reverse(
                "event-default-times",
                kwargs={"generation_id": self.club.current_generation.id},
            )
        )
        print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["start_datetime"], "2018-01-01T10:00:00")
        self.assertEqual(response.data["end_datetime"], "2018-01-01T11:00:00")
        self.assertEqual(response.data["start_minutes"], 0)
        self.assertEqual(response.data["late_minutes"], 10)
        self.assertEqual(response.data["fail_minutes"], 30)
