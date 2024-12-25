from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from userapp.models import User


class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            # AccessToken 객체에서 직접 payload 접근
            print("validated_token: ", validated_token)
            user_id = validated_token["user_id"]
            print("user_id: ", user_id)
            user = User.objects.get(id=user_id)
            return user
        except (User.DoesNotExist, KeyError) as e:
            print("error type: ", type(e))
            print("error: ", e)
            raise AuthenticationFailed(
                "User not found or token invalid", code="user_not_found"
            )
