from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('login', views.KakaoLoginView.as_view(), name='kakao_login'),
    path('refresh', TokenRefreshView.as_view(), name='token_refresh'),
]