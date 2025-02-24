from rest_framework.routers import DefaultRouter
from django.urls import path
from . import views

router = DefaultRouter()

router.register("generations", views.GenerationView, basename="generations")
router.register("members", views.MemberView, basename="members")
router.register("", views.ClubViewSet, basename="clubs")

urlpatterns = [
    path("apply/<int:apply_id>/", views.ClubApplyViewSet.as_view({"post": "approve", "delete": "reject"}), name="apply-detail"),
    path("apply/", views.ClubApplyViewSet.as_view({"post": "apply", "get": "list"}), name="apply-list"),
] + router.urls
