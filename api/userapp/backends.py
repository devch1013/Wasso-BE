from django.contrib.auth.backends import BaseBackend

from api.userapp.models import User


class CustomAuthBackend(BaseBackend):
    def authenticate(self, request, user_id=None):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
