from django.urls import path
from frontend.views import index

app_name = "frontend"

urlpatterns = [
    path("", index, name=""),
    path("join", index),
    path("create", index),
    path("info", index),
    path("room/<str:roomCode>", index),
]