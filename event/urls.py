from django.urls import path
from . import views

urlpatterns = [
    path('upcoming', views.EventListView.as_view(), name='event-list'),
    path('<int:event_id>', views.EventDetailView.as_view(), name='event-detail'),
    path('<int:event_id>/qr-check', views.EventQRCheckView.as_view(), name='event-qr-check'),
    path('<int:event_id>/attend', views.EventAttendanceView.as_view(), name='event-attend'),
]