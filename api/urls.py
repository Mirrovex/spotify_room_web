from django.urls import path
from api.views import ( main, ResetView, RoomView, CreateRoomView,
                      GetRoom, JoinRoomView, UserInRoomView,
                      LeaveRoomView, UpdateRoomView, UserView )

urlpatterns = [
    path("main/", main),
    path("reset/", ResetView.as_view()),
    path("room/", RoomView.as_view()),
    path("user/", UserView.as_view()),
    path("create-room/", CreateRoomView.as_view()),
    path("get-room/", GetRoom.as_view()),
    path("join-room/", JoinRoomView.as_view()),
    path("user-in-room/", UserInRoomView.as_view()),
    path("leave-room/", LeaveRoomView.as_view()),
    path("update-room/", UpdateRoomView.as_view()),
]