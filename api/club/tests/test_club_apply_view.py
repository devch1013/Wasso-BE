from api.userapp.models import Provider, User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from api.club.services.club_service import ClubService
from common.test_utils.image_utils import ImageTestUtils
from unittest.mock import patch
from api.club.models import ClubApply, GenMember


class ClubApplyViewTest(APITestCase):
    @patch("django.core.files.storage.default_storage.save")
    def setUp(self, mock_storage):
        mock_storage.return_value = "test-image-path.jpg"
        self.user = User.objects.create_user(
            identifier="testuser",
            username="testuser",
            provider=Provider.GOOGLE,
        )
        self.user2 = User.objects.create_user(
            identifier="testuser2",
            username="testuser2",
            provider=Provider.GOOGLE,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user2)
        self.club, self.member = ClubService.create_club(
            user=self.user,
            name="Test Club",
            image=ImageTestUtils.create_test_image(),
            description="Test Description",
            generation_data={
                "name": "Test Generation",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
            },
        )

    def test_create_club_apply(self):
        response = self.client.post(
            f"{reverse('apply-list')}?club-code={self.club.current_generation.invite_code}"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_approve_club_apply(self):
        club_apply = ClubApply.objects.create(
            user=self.user2,
            generation=self.club.current_generation,
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse("apply-detail", args=[club_apply.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            ClubApply.objects.filter(id=club_apply.id).first().accepted, True
        )

        club_apply.refresh_from_db()
        self.assertEqual(club_apply.accepted, True)
        self.assertIsNotNone(club_apply.accepted_at)

        self.club.refresh_from_db()
        self.assertEqual(self.club.members.count(), 2)
        generationMapping = GenMember.objects.filter(
            member__user=self.user2, generation=self.club.current_generation
        ).first()
        self.assertEqual(
            generationMapping.role,
            self.club.default_role,
        )
        
    def test_reject_club_apply(self):
        club_apply = ClubApply.objects.create(
            user=self.user2,
            generation=self.club.current_generation,
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse("apply-detail", args=[club_apply.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ClubApply.objects.filter(id=club_apply.id).exists(), False)