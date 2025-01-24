from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register("generation", views.GenerationView, basename="generation")
router.register("apply", views.ClubApplyViewSet, basename="apply")
router.register("member", views.MemberView, basename="member")
router.register("", views.ClubViewSet, basename="club")

urlpatterns = router.urls
