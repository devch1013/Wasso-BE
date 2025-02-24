from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from api.club.services.club_service import ClubService
from common.test_utils.image_utils import ImageTestUtils
from api.userapp.models import Provider, User

from ..models import Club, Generation, GenerationMapping, Member, Role, ClubApply


class ClubTestCase(APITestCase):
    @patch("django.core.files.storage.default_storage.save")
    def setUp(self, mock_storage):
        # S3 저장 mock 설정
        mock_storage.return_value = "test-image-path.jpg"

        # 테스트용 사용자 생성
        self.user = User.objects.create_user(
            identifier="test1234",
            username="test1234",
            provider=Provider.KAKAO,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    @patch("django.core.files.storage.default_storage.save")
    def test_create_club(self, mock_storage):
        """클럽 생성 테스트"""
        mock_storage.return_value = "test-image-path.jpg"
        data = {
            "name": "Test Club",
            "description": "Test Description",
            "image": ImageTestUtils.create_test_image(),
            "generation.name": "1기",
            "generation.start_date": "2024-01-01",
            "generation.end_date": "2024-12-31",
        }

        response = self.client.post(reverse("club-list"), data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Club.objects.count(), 1)
        self.assertEqual(Generation.objects.count(), 1)
        self.assertEqual(GenerationMapping.objects.count(), 1)
        self.assertEqual(Member.objects.count(), 1)
        self.assertEqual(Role.objects.count(), 3)

        # 생성된 클럽 확인
        club = Club.objects.first()
        self.assertEqual(club.name, "Test Club")

        # 사용자 권한 확인
        member = Member.objects.first()
        self.assertEqual(member.get_current_generation().generation.name, "1기")
        self.assertEqual(member.get_current_generation().role.name, "회장")

    def test_create_club_invalid_data(self):
        """클럽 생성 테스트(유효하지 않은 데이터)"""
        data = {
            "name": "",
            "description": "Test Description",
            "image": "image.jpg",
        }

        response = self.client.post(reverse("club-list"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            "name": "Hello",
            "description": "Test Description",
            "image": "",
        }
        response = self.client.post(reverse("club-list"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("django.core.files.storage.default_storage.save")
    def test_list_user_clubs(self, mock_storage):
        """사용자의 클럽 목록 조회 테스트"""
        mock_storage.return_value = "test-image-path.jpg"
        # 테스트용 클럽 생성
        ClubService.create_club(
            user=self.user,
            name="Test Club",
            image=ImageTestUtils.create_test_image(),
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
            image=ImageTestUtils.create_test_image(),
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
        club, user_club = ClubService.create_club(
            user=self.user,
            name="Test Club",
            image=ImageTestUtils.create_test_image(),
            description="Test Description",
            generation_data={
                "name": "1기",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
            },
        )
        response = self.client.get(reverse("club-detail", kwargs={"pk": club.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Club")

    def test_delete_club(self):
        """클럽 삭제 테스트"""
        club, user_club = ClubService.create_club(
            user=self.user,
            name="Test Club",
            image=ImageTestUtils.create_test_image(),
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
        self.assertEqual(GenerationMapping.objects.count(), 1)
        self.assertEqual(Member.objects.count(), 1)

        response = self.client.delete(reverse("club-detail", kwargs={"pk": club.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # 삭제 후 모든 관련 레코드 확인
        self.assertEqual(Club.objects.count(), 0)
        self.assertEqual(Generation.objects.count(), 0)
        self.assertEqual(GenerationMapping.objects.count(), 0)
        self.assertEqual(Member.objects.count(), 0)

    def test_delete_club_invalid_data(self):
        """클럽 삭제 테스트(유효하지 않은 데이터)"""
        response = self.client.delete(reverse("club-detail", kwargs={"pk": 9999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_club(self):
        """클럽 수정 테스트"""
        club, user_club = ClubService.create_club(
            user=self.user,
            name="Test Club",
            image=ImageTestUtils.create_test_image(),
            description="Test Description",
            generation_data={
                "name": "1기",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
            },
        )

        data = {
            "description": "Updated Description",
        }

        response = self.client.put(
            reverse("club-detail", kwargs={"pk": club.id}), data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["description"], "Updated Description")

        club.refresh_from_db()
        self.assertEqual(club.description, "Updated Description")

    @patch("django.core.files.storage.default_storage.save")
    def test_get_applies(self, mock_storage):
        """클럽 지원자 조회 테스트"""
        mock_storage.return_value = "test-image-path.jpg"
        club, member = ClubService.create_club(
            user=self.user,
            name="Test Club",
            image=ImageTestUtils.create_test_image(),
            description="Test Description",
            generation_data={
                "name": "1기",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
            },
        )
        user1 = User.objects.create_user(
            identifier="testuser1",
            username="testuser1",
            provider=Provider.KAKAO,
        )
        user2 = User.objects.create_user(
            identifier="testuser2",
            username="testuser2",
            provider=Provider.KAKAO,
        )
        ClubApply.objects.create(user=user1, generation=club.current_generation)
        ClubApply.objects.create(user=user2, generation=club.current_generation)
        response = self.client.get(reverse("club-applies", kwargs={"pk": club.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["user"]["username"], "testuser1")
        self.assertEqual(response.data[1]["user"]["username"], "testuser2")

    def test_get_roles(self):
        """클럽 역할 조회 테스트"""
        club, member = ClubService.create_club(
            user=self.user,
            name="Test Club",
            image=ImageTestUtils.create_test_image(),
            description="Test Description",
            generation_data={
                "name": "1기",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
            },
        )
        response = self.client.get(reverse("club-roles", kwargs={"pk": club.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0]["name"], "회장")
        self.assertEqual(response.data[1]["name"], "임원진")
        self.assertEqual(response.data[2]["name"], "회원")

    def test_get_generations(self):
        """클럽 기수 조회 테스트"""
        club, member = ClubService.create_club(
            user=self.user,
            name="Test Club",
            image=ImageTestUtils.create_test_image(),
            description="Test Description",
            generation_data={
                "name": "1기",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
            },
        )
        response = self.client.get(reverse("club-generations", kwargs={"pk": club.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "1기")
        self.assertEqual(response.data[0]["start_date"], "2024-01-01")
        self.assertEqual(response.data[0]["end_date"], "2024-12-31")
