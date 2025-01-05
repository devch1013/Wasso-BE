from abc import ABC, abstractmethod

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
            if not user.check_password(password):
                raise ValueError("잘못된 비밀번호입니다.")
            return user
        except User.DoesNotExist:
            # 새 사용자 생성
            user = User.objects.create_user(
                username="none",
                identifier=identifier,
                password=password,
            )
            return user


class KakaoAuthService(AuthService):
    def get_or_create_user(self, code: str):
        pass
