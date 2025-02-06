from abc import ABC, abstractmethod

import requests
from rest_framework_simplejwt.tokens import RefreshToken

from main.exceptions import CustomException, ErrorCode
from userapp.models import User


class AuthService(ABC):
    @abstractmethod
    def get_or_create_user(self, identifier: str, password: str):
        pass

    def get_token(self, user: User):
        print(user)
        return RefreshToken.for_user(user)


class NativeAuthService(AuthService):
    def get_or_create_user(self, identifier: str, password: str):
        try:
            # 기존 사용자 찾기
            user = User.objects.get(identifier=identifier)
            # 비밀번호 확인
            if not user.password == password:
                raise ValueError("잘못된 비밀번호입니다.")
            return user
        except User.DoesNotExist:
            # 새 사용자 생성
            user = User.objects.create(
                identifier=identifier,
                password=password,
            )
            return user


class KakaoAuthService(AuthService):
    def get_or_create_user(self, identifier: str, password: str = None):
        return self._create_user(identifier)

    def _get_kakao_user_info(self, access_token):
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
        }
        response = requests.get("https://kapi.kakao.com/v2/user/me", headers=headers)
        if response.status_code == 200:
            return response.json()
        return None

    def _create_user(self, kakao_token):
        if not kakao_token:
            raise CustomException(ErrorCode.INVALID_TOKEN)

        # 카카오 API로 사용자 정보 가져오기
        user_info = self._get_kakao_user_info(kakao_token)
        if not user_info:
            raise CustomException(ErrorCode.INVALID_TOKEN)

        # 사용자 생성 또는 조회
        user, _ = User.objects.get_or_create(
            identifier=str(user_info["id"]),
            defaults={
                "username": user_info.get("properties", {}).get("nickname", ""),
            },
        )

        return user


class GoogleAuthService(AuthService):
    def get_or_create_user(self, identifier: str, password: str = None):
        return self._create_user(identifier)

    def _get_google_user_info(self, access_token):
        headers = {
            "Authorization": f"Bearer {access_token}",
        }
        response = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo", headers=headers
        )
        if response.status_code == 200:
            return response.json()
        return None

    def _create_user(self, google_token):
        print(google_token)
        if not google_token:
            raise CustomException(ErrorCode.INVALID_TOKEN)

        # Google API로 사용자 정보 가져오기
        user_info = self._get_google_user_info(google_token)
        if not user_info:
            raise CustomException(ErrorCode.INVALID_TOKEN)

        # 사용자 생성 또는 조회
        user, _ = User.objects.get_or_create(
            identifier=user_info["sub"],  # Google의 고유 사용자 ID
            defaults={
                "username": user_info.get("name", ""),
                "email": user_info.get("email", ""),
            },
        )

        return user
