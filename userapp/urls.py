from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path("login", views.KakaoLoginView.as_view({"post": "create"}), name="kakao_login"),
    path("refresh", TokenRefreshView.as_view(), name="token_refresh"),
]
