from datetime import date, datetime, timedelta

from rest_framework.test import APITestCase

from club.models import Club, Generation, Position, UserClub
from userapp.models import User

from ..models import AttendanceType, Event


class EventViewSetTests(APITestCase):
    def setUp(self):
        # 테스트에 필요한 데이터 설정
        self.user = User.objects.create_user(
            username="testuser",
            identifier="testuser",
        )
        self.club = Club.objects.create(name="Test Club")
        self.generation = Generation.objects.create(
            name="Test Generation",
            club=self.club,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
        )
        self.club_admin = UserClub.objects.create(
            user=self.user,
            club=self.club,
            current_role=Position.OWNER,
            last_generation=self.generation,
        )
        self.event = Event.objects.create(
            generation=self.generation,
            name="Test Event",
            description="Test Description",
            start_datetime=datetime.now(),
            end_datetime=datetime.now() + timedelta(hours=1),
            attendance_start_datetime=datetime.now(),
            attendance_end_datetime=datetime.now() + timedelta(hours=1),
            begin_minutes=10,
            late_tolerance_minutes=15,
            location="Test Location",
            latitude=37.565815,
            longitude=126.972366,
            qr_code_url="https://example.com/qrcode",
            qr_code="1234567890",
            attendance_type=AttendanceType.BOTH,
        )

    # def test_list_events(self):
    #     # 로그인
    #     self.client.force_authenticate(user=self.user)

    #     # API 호출
    #     url = reverse("event-list")
    #     response = self.client.get(f"{url}?clubId={self.club.id}")

    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(response.data), 1)
    #     self.assertEqual(response.data[0]["title"], "Test Event")

    # def test_create_event_as_admin(self):
    #     self.client.force_authenticate(user=self.user)

    #     event_data = {
    #         "name": "New Event",
    #         "description": "New Description",
    #         "generation": self.generation.id,
    #     }

    #     url = reverse("event-list")
    #     response = self.client.post(url, event_data)

    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(response.data["title"], "New Event")
    #     self.assertEqual(Event.objects.count(), 1)

    # # ... 나머지 테스트 메서드들
