from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from club.models import Club, Generation, UserGeneration, UserClub, Position

User = get_user_model()


class ClubTestCase(APITestCase):
    def setUp(self):
        # 테스트용 사용자 생성
        self.user = User.objects.create_user(
            email="test@example.com",
            identifier="test1234",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # API 엔드포인트
        self.create_url = reverse("club-list")

    def test_create_club(self):
        """클럽 생성 테스트"""
        data = {
            "name": "Test Club",
            "description": "Test Description",
            "image_url": "http://example.com/image.jpg",
            "generation": {
                "name": "1기",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
            },
        }

        response = self.client.post(self.create_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Club.objects.count(), 1)
        self.assertEqual(Generation.objects.count(), 1)
        self.assertEqual(UserGeneration.objects.count(), 1)
        self.assertEqual(UserClub.objects.count(), 1)

        # 생성된 클럽 확인
        club = Club.objects.first()
        self.assertEqual(club.name, "Test Club")

        # 사용자 권한 확인
        user_club = UserClub.objects.first()
        self.assertEqual(user_club.current_role, Position.OWNER.value)

    def test_list_user_clubs(self):
        """사용자의 클럽 목록 조회 테스트"""
        # 테스트용 클럽 생성
        club = Club.objects.create(name="Test Club", description="Test Description")
        generation = Generation.objects.create(
            club=club, name="1기", start_date="2024-01-01", end_date="2024-12-31"
        )
        UserClub.objects.create(
            user=self.user,
            club=club,
            last_generation=generation,
            current_role=Position.OWNER.value,
        )

        response = self.client.get(reverse("club-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["club"]["name"], "Test Club")
