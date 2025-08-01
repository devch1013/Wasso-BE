from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from api.club.services.club_service import ClubService
from api.userapp.models import User
from common.test_utils.image_utils import ImageTestUtils


class MemberViewTest(APITestCase):
    @patch("django.core.files.storage.default_storage.save")
    def setUp(self, mock_storage):
        mock_storage.return_value = "test-image-path.jpg"
        self.user = User.objects.create_user(username="testuser", identifier="testuser")
        self.club, self.member = ClubService.create_club(
            name="Test Club",
            description="Test Description",
            image=ImageTestUtils.create_test_image(),
            user=self.user,
            generation_data={
                "name": "Test Generation",
                "start_date": "2021-01-01",
                "end_date": "2021-01-01",
            },
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_add_tag(self):
        url = reverse("members-tag", kwargs={"pk": self.member.id})
        response = self.client.put(url, {"tag": "test-tag"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.member.refresh_from_db()
        self.assertIn("test-tag", self.member.tags)

    def test_remove_tag(self):
        self.member.tags.append("test-tag")
        self.member.save()
        url = reverse("members-tag", kwargs={"pk": self.member.id})
        response = self.client.delete(url, {"tag": "test-tag"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.member.refresh_from_db()
        self.assertNotIn("test-tag", self.member.tags)

    def test_update_description(self):
        url = reverse("members-description", kwargs={"pk": self.member.id})
        response = self.client.put(url, {"description": "test-description"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.member.refresh_from_db()
        self.assertEqual(self.member.description, "test-description")
