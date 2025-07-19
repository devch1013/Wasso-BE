from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from api.userapp import views

urlpatterns = [
    path(
        "", views.UserView.as_view({"get": "retrieve", "put": "update"}), name="user-me"
    ),
    path(
        "push/",
        views.UserView.as_view({"post": "push", "get": "push"}),
        name="push",
    ),
    path(
        "push-test/",
        views.UserView.as_view({"post": "push_test"}),
        name="push-test",
    ),
    path(
        "<str:provider>/login/",
        views.SocialAuthView.as_view({"post": "create"}),
        name="social-login",
    ),
    path(
        "withdraw/",
        views.SocialAuthView.as_view({"delete": "withdraw"}),
        name="withdraw",
    ),
    path("refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("session", views.PcSessionView.as_view(), name="pc-session"),
]
