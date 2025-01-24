from abc import ABC, abstractmethod

import requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from userapp.models import User


class AuthService(ABC):
    @abstractmethod
    def get_or_create_user(self, identifier: str, password: str):
        pass

    def get_token(self, user: User):
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
            return Response(
                {"error": "Kakao token is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # 카카오 API로 사용자 정보 가져오기
        user_info = self._get_kakao_user_info(kakao_token)
        if not user_info:
            return Response(
                {"error": "Invalid Kakao token"}, status=status.HTTP_401_UNAUTHORIZED
            )

        # 사용자 생성 또는 조회
        user, _ = User.objects.get_or_create(
            identifier=str(user_info["id"]),
            defaults={
                "username": user_info.get("properties", {}).get("nickname", ""),
            },
        )

        return user
