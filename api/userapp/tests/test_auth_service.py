from unittest.mock import MagicMock, patch

import pytest
from django.test import TestCase

from api.userapp.service.auth import GoogleAuthService, KakaoAuthService
from common.exceptions import CustomException


class TestKakaoAuthService(TestCase):
    def setUp(self):
        self.service = KakaoAuthService()
        self.mock_kakao_response = {
            "id": 123456789,
            "properties": {"nickname": "테스트유저"},
        }

    @patch("requests.get")
    def test_get_or_create_user_success(self, mock_get):
        # Mock 설정
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_kakao_response
        mock_get.return_value = mock_response

        # 테스트 실행
        user = self.service.get_or_create_user("fake_token")

        # 검증
        self.assertEqual(user.identifier, "123456789")
        self.assertEqual(user.username, "테스트유저")

    @patch("requests.get")
    def test_get_or_create_user_invalid_token(self, mock_get):
        # Mock 설정
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        # 테스트 실행 및 검증
        with pytest.raises(CustomException):
            self.service.get_or_create_user("invalid_token")

    def test_get_or_create_user_empty_token(self):
        with pytest.raises(CustomException):
            self.service.get_or_create_user("")


class TestGoogleAuthService(TestCase):
    def setUp(self):
        self.service = GoogleAuthService()
        self.mock_google_response = {
            "sub": "12345",
            "name": "Test User",
            "email": "test@example.com",
        }

    @patch("requests.get")
    def test_get_or_create_user_success(self, mock_get):
        # Mock 설정
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_google_response
        mock_get.return_value = mock_response

        # 테스트 실행
        user = self.service.get_or_create_user("fake_token")

        # 검증
        self.assertEqual(user.identifier, "12345")
        self.assertEqual(user.username, "Test User")
        self.assertEqual(user.email, "test@example.com")

    @patch("requests.get")
    def test_get_or_create_user_invalid_token(self, mock_get):
        # Mock 설정
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        # 테스트 실행 및 검증
        with pytest.raises(CustomException):
            self.service.get_or_create_user("invalid_token")

    def test_get_or_create_user_empty_token(self):
        with pytest.raises(CustomException):
            self.service.get_or_create_user("")
