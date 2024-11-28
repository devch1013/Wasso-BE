from django.urls import path
from . import views

urlpatterns = [
    path('', views.ClubListView.as_view(), name='club-list'),
]