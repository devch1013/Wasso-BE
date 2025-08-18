from django.urls import path

from api.event import views

urlpatterns = [
    path(
        "",
        views.EventViewSet.as_view({"post": "create", "get": "all_events"}),
        name="event-list",
    ),
    path(
        "upcoming/",
        views.EventViewSet.as_view({"get": "upcoming"}),
        name="event-upcoming",
    ),
    path(
        "edit-request/<int:pk>/",
        views.EditRequestView.as_view({"post": "approve"}),
        name="event-edit-request-approve",
    ),
    path(
        "absent-apply/<int:pk>/",
        views.AbsentApplyView.as_view({"post": "approve"}),
        name="absent-apply-approve",
    ),
    path(
        "<int:pk>/",
        views.EventViewSet.as_view(
            {"get": "retrieve", "put": "update", "delete": "destroy"}
        ),
        name="event-detail",
    ),
    path(
        "<int:event_id>/generation-info/",
        views.EventViewSet.as_view({"get": "generation_info"}),
        name="event-generation-info",
    ),
    path(
        "<int:event_id>/attendance/all/",
        views.EventAttendanceView.as_view({"post": "attendance_all"}),
        name="event-attendance-all",
    ),
    path(
        "<int:event_id>/attendance/me/",
        views.EventAttendanceView.as_view({"get": "me"}),
        name="event-attendance-me",
    ),
    path(
        "<int:event_id>/attendance/<int:gen_member_id>/",
        views.EventAttendanceView.as_view({"get": "get_member_log"}),
        name="event-attendance-log",
    ),
    path(
        "<int:event_id>/attendance/",
        views.EventAttendanceView.as_view(
            {"post": "create", "get": "attendances", "put": "modify"}
        ),
        name="event-attendance",
    ),
    path(
        "<int:event_id>/absent-apply/",
        views.AbsentApplyView.as_view({"post": "create", "get": "list"}),
        name="event-absent-apply",
    ),
    path(
        "<int:event_id>/edit-request/",
        views.EditRequestView.as_view({"post": "create", "get": "list"}),
        name="event-edit-request",
    ),
]
