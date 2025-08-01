from abc import ABC, abstractmethod
from datetime import datetime, timedelta

import requests
from django.conf import settings
from jose import jwt
from rest_framework_simplejwt.tokens import RefreshToken

from api.userapp.models import User
from common.exceptions import CustomException, ErrorCode


class AuthService(ABC):
    @abstractmethod
    def get_or_create_user(self, identifier: str, fcmToken: str, name: str = None):
        pass

    def get_token(self, user: User):
        print(user)
        return RefreshToken.for_user(user)


class GoogleAuthService(AuthService):
    def get_or_create_user(self, identifier: str, fcmToken: str, name: str = None):
        return self._create_user(identifier, fcmToken, name)

    def _get_google_user_info(self, access_token):
        headers = {
            "Authorization": f"Bearer {access_token}",
        }
        response = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo", headers=headers
        )
        if response.status_code == 200:
            print(response.json())
            return response.json()
        return None

    def _create_user(self, google_token, fcmToken, name):
        if not google_token:
            raise CustomException(ErrorCode.INVALID_TOKEN)

        # Google API로 사용자 정보 가져오기
        user_info = self._get_google_user_info(google_token)
        if not user_info:
            raise CustomException(ErrorCode.INVALID_TOKEN)

        # 사용자 생성 또는 조회
        user, is_created = User.objects.get_or_create(
            identifier=user_info["sub"],  # Google의 고유 사용자 ID
            defaults={
                "username": user_info.get("name", ""),
                "email": user_info.get("email", ""),
                "provider": "google",
            },
        )

        if fcmToken:
            user.fcm_token = fcmToken
            user.save()

        return user


class AppleAuthService(AuthService):
    def __init__(self):
        self.team_id = settings.APPLE_TEAM_ID
        self.key_id = settings.APPLE_KEY_ID
        self.bundle_id = settings.APPLE_BUNDLE_ID

    def _format_private_key(self, private_key: str) -> str:
        """Convert private key to PEM format"""
        if "-----BEGIN PRIVATE KEY-----" not in private_key:
            # Add PEM headers and footer if they're missing
            formatted_key = (
                "-----BEGIN PRIVATE KEY-----\n"
                f"{private_key}\n"
                "-----END PRIVATE KEY-----"
            )
            return formatted_key
        return private_key

    def get_or_create_user(self, identifier: str, fcmToken: str, name: str = None):
        return self._create_user(identifier, fcmToken, name)

    def _get_apple_user_info(self, identity_token):
        try:
            decoded = jwt.decode(
                identity_token,
                "",  # 애플 공개키로 검증하므로 빈 문자열 사용
                options={
                    "verify_signature": False,  # 서명 확인 건너뛰기
                    "verify_aud": True,
                },
                audience=self.bundle_id,  # 환경변수에서 가져온 bundle_id 사용
            )
            return decoded
        except Exception as e:
            print(f"Error decoding Apple token: {e}")
            return None

    def _create_user(self, identity_token, fcmToken, name):
        if not identity_token:
            raise CustomException(ErrorCode.INVALID_TOKEN)

        # Apple ID token으로 사용자 정보 가져오기
        user_info = self._get_apple_user_info(identity_token)
        if not user_info:
            raise CustomException(ErrorCode.INVALID_TOKEN)

        # 사용자 생성 또는 조회
        user, is_created = User.objects.get_or_create(
            identifier=user_info["sub"],  # Apple의 고유 사용자 ID
            defaults={
                "email": user_info.get("email", ""),
                "provider": "apple",
                "username": name,
            },
        )

        if fcmToken:
            user.fcm_token = fcmToken
            user.save()

        return user

    def revoke_apple_token(self, user_identifier: str):
        """애플 계정 연동 해제"""
        try:
            # 클라이언트 시크릿 생성
            client_secret = self._create_client_secret()

            # Apple 토큰 철회 엔드포인트
            url = "https://appleid.apple.com/auth/revoke"

            headers = {"Content-Type": "application/x-www-form-urlencoded"}

            data = {
                "client_id": self.bundle_id,
                "client_secret": client_secret,
                "token": user_identifier,  # 사용자의 identifier (sub 값)
                "token_type_hint": "access_token",
            }

            response = requests.post(url, headers=headers, data=data)

            if response.status_code == 200:
                # 성공적으로 철회된 경우 사용자 삭제
                return True
            return False

        except Exception as e:
            print(f"Error revoking Apple token: {e}")
            return False

    def _create_client_secret(self):
        """Apple Client Secret 생성"""
        now = datetime.utcnow()
        exp_time = now + timedelta(days=180)  # 180일 유효기간

        headers = {"kid": self.key_id, "alg": "ES256"}

        payload = {
            "iss": self.team_id,
            "iat": now,
            "exp": exp_time,
            "aud": "https://appleid.apple.com",
            "sub": self.bundle_id,
        }

        # JWT 토큰 생성
        client_secret = jwt.encode(
            payload, self.private_key, algorithm="ES256", headers=headers
        )

        return client_secret


class NativeAuthService(AuthService):
    def get_or_create_user(self, identifier: str, password: str):
        if not identifier or not password:
            raise CustomException(ErrorCode.INVALID_TOKEN)

        user, is_created = User.objects.get_or_create(
            identifier=identifier,
            defaults={
                "password": password,
                "username": identifier,
                "provider": "native",
            },
        )

        return user
