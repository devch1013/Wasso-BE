from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"", views.EventViewSet, basename="event")
router.register(r"qr-check", views.EventQRCheckView, basename="event-qr-check")

urlpatterns = router.urls
