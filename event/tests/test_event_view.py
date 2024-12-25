from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from club.models import Club, UserClub, Position
from userapp.models import User
from event.models import Event


class EventViewSetTests(APITestCase):
    def setUp(self):
        # 테스트에 필요한 데이터 설정
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.club = Club.objects.create(name="Test Club")
        self.club_admin = UserClub.objects.create(
            user=self.user, club=self.club, current_role=Position.OWNER
        )
        self.event = Event.objects.create(
            title="Test Event", description="Test Description", club=self.club
        )

    def test_list_events(self):
        # 로그인
        self.client.force_authenticate(user=self.user)

        # API 호출
        url = reverse("event-list")
        response = self.client.get(f"{url}?clubId={self.club.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Test Event")

    def test_create_event_as_admin(self):
        self.client.force_authenticate(user=self.user)

        event_data = {
            "title": "New Event",
            "description": "New Description",
            "club": self.club.id,
        }

        url = reverse("event-list")
        response = self.client.post(url, event_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "New Event")
        self.assertEqual(Event.objects.count(), 1)
