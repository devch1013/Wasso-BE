from django.urls import path

from api.notion import views

urlpatterns = [
    path(
        "",
        views.NotionViewSet.as_view({"post": "create"}),
        name="notion-list",
    ),
]
