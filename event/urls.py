from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("attendance", views.EventAttendanceView, basename="event-attendance")
router.register(r"", views.EventViewSet, basename="event")

urlpatterns = router.urls
