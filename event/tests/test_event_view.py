from datetime import timedelta
from unittest.mock import patch

from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase

from club.services.club_service import ClubService
from event.models import Event
from main.test_utils.image_utils import ImageTestUtils
from userapp.models import User


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

    @patch("django.core.files.storage.default_storage.save")
    def test_create_event(self, mock_storage):
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
            "start_minute": 0,
            "late_minute": 10,
            "fail_minute": 30,
        }
        response = self.client.post(reverse("event-list"), data, format="multipart")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Event.objects.first().title, "Test Event")
        self.assertEqual(Event.objects.first().description, "Test Event Description")
        self.assertEqual(Event.objects.first().location, "Test Location")
        self.assertEqual(len(Event.objects.first().images), 1)

    @patch("django.core.files.storage.default_storage.save")
    def test_update_event(self, mock_storage):
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
