from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register("apply", views.ClubApplyViewSet, basename="apply")
router.register("", views.ClubViewSet, basename="club")

urlpatterns = router.urls
