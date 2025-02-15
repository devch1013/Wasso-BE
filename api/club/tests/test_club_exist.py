from unittest.mock import patch

from rest_framework.test import APIClient, APITestCase

from api.club.services.club_service import ClubService
from config.test_utils.image_utils import ImageTestUtils
from api.userapp.models import Provider, User


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

        image = ImageTestUtils.create_test_image()

        self.club, self.member = ClubService.create_club(
            user=self.user,
            name="Test Club",
            image=image,
            description="Test Description",
            generation_data={
                "name": "1기",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
            },
        )
