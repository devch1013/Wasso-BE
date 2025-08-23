from django.urls import path
from rest_framework.routers import DefaultRouter

from api.club import views

router = DefaultRouter()

router.register("generations", views.GenerationView, basename="generations")
router.register("members", views.MemberView, basename="members")
router.register("gen-members", views.GenMemberView, basename="gen-members")
# router.register("apply", views.ClubApplyView, basename="apply")
router.register("", views.ClubView, basename="clubs")

urlpatterns = router.urls

urlpatterns = [
    path(
        "apply/<int:apply_id>/",
        views.ClubApplyView.as_view({"post": "approve", "delete": "reject"}),
        name="apply-detail",
    ),
    path(
        "apply/",
        views.ClubApplyView.as_view({"post": "apply", "get": "list"}),
        name="apply-list",
    ),
    path(
        "apply/info/",
        views.ClubApplyView.as_view({"get": "get_info"}),
        name="apply-info",
    ),
    path(
        "apply/notice-test/",
        views.ClubApplyView.as_view({"get": "notice_test"}),
        name="apply-notice-test",
    ),
] + router.urls
