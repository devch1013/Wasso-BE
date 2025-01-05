from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path(
        "", views.UserView.as_view({"get": "retrieve", "put": "update"}), name="user_me"
    ),
    path(
        "<str:provider>/login",
        views.SocialAuthView.as_view({"post": "create"}),
        name="kakao_login",
    ),
    path("refresh", TokenRefreshView.as_view(), name="token_refresh"),
]
