from django.urls import path
from spotify.views import *

urlpatterns = [
    path("get-auth-url", AuthURLView.as_view()),
    path("get-token", GetTokenView.as_view()),
    path("redirect", spotify_callback),
    path("is-auth", IsAuthView.as_view()),
    path("current-song", CurrentSongView.as_view()),
    path("pause-song", PauseSongView.as_view()),
    path("play-song", PlaySongView.as_view()),
    path("next-song", NextSongView.as_view()),
]