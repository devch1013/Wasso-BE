from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"", views.EventViewSet, basename="event")

urlpatterns = [
    path(
        "<int:event_id>/qr-check",
        views.EventQRCheckView.as_view(),
        name="event-qr-check",
    ),
    path(
        "<int:event_id>/attend",
        views.EventAttendanceView.as_view(),
        name="event-attend",
    ),
]

urlpatterns += router.urls
