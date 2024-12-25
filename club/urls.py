from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"clubs", views.ClubViewSet, basename="club")

urlpatterns = router.urls
