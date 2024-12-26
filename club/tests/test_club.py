from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from club.services.club_service import ClubService

from ..models import Club, Generation, Position, UserClub, UserGeneration

User = get_user_model()


class ClubTestCase(APITestCase):
    def setUp(self):
        # 테스트용 사용자 생성
        self.user = User.objects.create_user(
            email="test@example.com",
            username="test1234",
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

        response = self.client.post(reverse("club-list"), data, format="json")

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

    def test_create_club_invalid_data(self):
        """클럽 생성 테스트(유효하지 않은 데이터)"""
        data = {
            "name": "",
            "description": "Test Description",
            "image_url": "http://example.com/image.jpg",
        }

        response = self.client.post(reverse("club-list"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            "name": "Hello",
            "description": "Test Description",
            "image_url": "",
        }
        response = self.client.post(reverse("club-list"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_user_clubs(self):
        """사용자의 클럽 목록 조회 테스트"""
        # 테스트용 클럽 생성
        ClubService.create_club(
            user=self.user,
            name="Test Club",
            image_url="http://example.com/image.jpg",
            description="Test Description",
            generation_data={
                "name": "1기",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
            },
        )

        ClubService.create_club(
            user=self.user,
            name="Test Club2",
            image_url="http://example.com/image.jpg",
            description="Test Description",
            generation_data={
                "name": "1기",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
            },
        )

        response = self.client.get(reverse("club-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["club_name"], "Test Club")

    def test_retrieve_club(self):
        """클럽 상세 조회 테스트"""
        club = ClubService.create_club(
            user=self.user,
            name="Test Club",
            image_url="http://example.com/image.jpg",
            description="Test Description",
            generation_data={
                "name": "1기",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
            },
        )
        response = self.client.get(reverse("club-detail", kwargs={"pk": club.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["club_name"], "Test Club")

    def test_delete_club(self):
        """클럽 삭제 테스트"""
        club = ClubService.create_club(
            user=self.user,
            name="Test Club",
            image_url="http://example.com/image.jpg",
            description="Test Description",
            generation_data={
                "name": "1기",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
            },
        )

        # 삭제 전 관련 레코드 수 확인
        self.assertEqual(Club.objects.count(), 1)
        self.assertEqual(Generation.objects.count(), 1)
        self.assertEqual(UserGeneration.objects.count(), 1)
        self.assertEqual(UserClub.objects.count(), 1)

        response = self.client.delete(reverse("club-detail", kwargs={"pk": club.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # 삭제 후 모든 관련 레코드 확인
        self.assertEqual(Club.objects.count(), 0)
        self.assertEqual(Generation.objects.count(), 0)
        self.assertEqual(UserGeneration.objects.count(), 0)
        self.assertEqual(UserClub.objects.count(), 0)

    def test_delete_club_invalid_data(self):
        """클럽 삭제 테스트(유효하지 않은 데이터)"""
        response = self.client.delete(reverse("club-detail", kwargs={"pk": 9999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_club(self):
        """클럽 수정 테스트"""
        club = ClubService.create_club(
            user=self.user,
            name="Test Club",
            image_url="http://example.com/image.jpg",
            description="Test Description",
            generation_data={
                "name": "1기",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
            },
        )

        data = {
            "description": "Updated Description",
            "image_url": "http://example.com/updated_image.jpg",
        }

        response = self.client.put(
            reverse("club-detail", kwargs={"pk": club.id}), data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["description"], "Updated Description")
        self.assertEqual(
            response.data["image_url"], "http://example.com/updated_image.jpg"
        )

        club.refresh_from_db()
        self.assertEqual(club.description, "Updated Description")
        self.assertEqual(club.image_url, "http://example.com/updated_image.jpg")
