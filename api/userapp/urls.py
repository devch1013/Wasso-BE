from django.urls import path

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
    path(
        "refresh/", views.RefreshView.as_view({"post": "refresh"}), name="token_refresh"
    ),
    path("session", views.PcSessionView.as_view({"post": "create"}), name="pc-session"),
    path(
        "session/authenticate",
        views.PcSessionView.as_view({"post": "authenticate"}),
        name="pc-session-authenticate",
    ),
    path(
        "session/<str:session_id>",
        views.PcSessionView.as_view({"get": "authenticate_check"}),
        name="pc-session-authenticate-check",
    ),
]
