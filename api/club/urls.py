from rest_framework.routers import DefaultRouter
from django.urls import path
from . import views

router = DefaultRouter()

router.register("generation", views.GenerationView, basename="generation")
router.register("member", views.MemberView, basename="member")
router.register("", views.ClubViewSet, basename="club")

urlpatterns = [
    path("apply/<int:apply_id>/", views.ClubApplyViewSet.as_view({"post": "approve", "delete": "reject"}), name="apply-detail"),
    path("apply/", views.ClubApplyViewSet.as_view({"post": "apply"}), name="apply-list"),
] + router.urls
