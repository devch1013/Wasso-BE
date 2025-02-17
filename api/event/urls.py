from django.urls import path
from . import views

urlpatterns = [
    path(
        "events/",
        views.EventViewSet.as_view({"post": "create"}),
        name="event-list",
    ),
    path(
        "events/upcoming/",
        views.EventViewSet.as_view({"get": "upcoming"}),
        name="event-upcoming",
    ),
    path(
        "events/<int:pk>/",
        views.EventViewSet.as_view({"get": "retrieve", "put": "update", "delete": "destroy"}),
        name="event-detail",
    ),
    path(
        "events/<int:event_id>/attendance/",
        views.EventAttendanceView.as_view({"post": "create", "get": "attendances", "put": "modify"}),
        name="event-attendance",
    ),
]
