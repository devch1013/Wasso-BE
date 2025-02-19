from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from api.userapp.models import User
from common.test_utils.image_utils import ImageTestUtils


class UserViewTest(APITestCase):
    def setUp(self):
        self.test_identifier = "testuser"
        self.user = User.objects.create_user(
            identifier=self.test_identifier, username="Test User"
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("user-me")

    def test_retrieve_user(self):
        """사용자 정보 조회 테스트"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "Test User")
        self.assertEqual(response.data["email"], None)
        self.assertEqual(response.data["phone_number"], None)
        self.assertEqual(response.data["profile_image"], None)

    @patch("django.core.files.storage.default_storage.save")
    def test_update_user(self, mock_storage):
        """사용자 정보 업데이트 테스트"""
        mock_storage.return_value = "test-image-path.jpg"

        update_data = {
            "username": "Updated Username",
            "email": "test@example.com",
            "phone_number": "010-1234-5678",
            "profile_image": ImageTestUtils.create_test_image(),
        }

        response = self.client.put(self.url, update_data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "Updated Username")
        self.assertEqual(response.data["email"], "test@example.com")
        self.assertEqual(response.data["phone_number"], "010-1234-5678")
        self.assertTrue(response.data["profile_image"].startswith("https://"))
        self.assertTrue(response.data["profile_image"].endswith(".png"))

        # DB에 실제로 업데이트되었는지 확인
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "Updated Username")
        self.assertEqual(self.user.email, "test@example.com")
        self.assertEqual(self.user.phone_number, "010-1234-5678")
        self.assertTrue(self.user.profile_image.url.startswith("https://"))
        self.assertTrue(self.user.profile_image.url.endswith(".png"))

    def test_update_user_unauthenticated(self):
        """인증되지 않은 사용자의 업데이트 시도 테스트"""
        self.client.force_authenticate(user=None)
        update_data = {"username": "Updated Username"}

        response = self.client.put(self.url, update_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
