from django.shortcuts import render, redirect
from spotify.credentials import CLIENT_ID, CLIENT_SECRET, REDIRECT_URL
from rest_framework.views import APIView
from requests import Request, post
from rest_framework import status
from rest_framework.response import Response
import base64

from api.models import Room
from spotify.models import Vote, SpotifyToken
from spotify.utils import *

class AuthURLView(APIView):
    def get(self, request, format=None):
        scopes = "user-read-playback-state user-modify-playback-state user-read-currently-playing"

        url = Request("GET", "https://accounts.spotify.com/authorize", params={
            "scope": scopes,
            "response_type": "code",
            "redirect_uri": REDIRECT_URL,
            "client_id": CLIENT_ID
        }).prepare().url

        return Response({"url": url}, status=status.HTTP_200_OK)
    

def spotify_callback(request, format=None):
    code = request.GET.get("code")
    error = request.GET.get("error")

    response = post("https://accounts.spotify.com/api/token",
                    data={
        "content-type": "application/x-www-form-urlencoded",
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URL,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }).json()

    access_token = response.get("access_token")
    token_type = response.get("token_type")
    refresh_token = response.get("refresh_token")
    expires_in = response.get("expires_in")
    error = response.get("error")

    if error:
        return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

    if not request.session.exists(request.session.session_key):
        request.session.create()

    update_or_create_user_tokens(request.session.session_key, access_token, token_type, expires_in, refresh_token)

    return redirect("frontend:")  # home


class IsAuthView(APIView):
    def get(self, request, format=None):
        is_auth = is_spotify_auth(self.request.session.session_key)
        return Response({"status": is_auth}, status=status.HTTP_200_OK)
    

class GetTokenView(APIView):
    def get(self, request, format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        user_token = SpotifyToken.objects.filter(user=self.request.session.session_key)
        if user_token.exists():
            return Response({"access_token": user_token[0].access_token}, status=status.HTTP_200_OK)
        return Response({"Not Found": ""}, status=status.HTTP_404_NOT_FOUND)
    

class CurrentSongView(APIView):
    def get(self, request, format=None):
        room_code = self.request.session.get("room_code")
        room = Room.objects.filter(code=room_code)
        if room.exists():
            room = room[0]
        else:
            return Response({"Not Found": "You are not a host of any room"}, status=status.HTTP_404_NOT_FOUND)
        
        host = room.host
        endpoint = "player/currently-playing"
        response = execute_spotify_api_request(host, endpoint)

        if "error" in response or "item" not in response:
            return Response({"Message": "Nothing playing", "Error": response.get("error")}, status=status.HTTP_204_NO_CONTENT)

        item = response.get("item")
        duration = item.get("duration_ms")
        progress = response.get("progress_ms")
        album_cover = item.get("album").get("images")[0].get("url")
        is_playing = response.get("is_playing")
        song_id = item.get("id")

        # return Response(response, status=status.HTTP_200_OK)

        artists_string = ""
        for i, artist in enumerate(item.get("artists")):
            if i > 0:
                artists_string += ", "
            artists_string += artist.get("name")

        song = {
            "id": song_id,
            "title": item.get("name"),
            "artists": artists_string,
            "duration": duration,
            "time": progress,
            "is_playing": is_playing,
            "image_url": album_cover,
            "votes": len(Vote.objects.filter(room=room, song_id=song_id)),
            "votes_needed": room.votes_to_skip
        }

        self.update_room_song(room, song_id)
            
        return Response(song, status=status.HTTP_200_OK)
    
    def update_room_song(self, room, song_id):
        current_song = room.current_song
        if current_song != song_id:
            room.current_song = song_id
            room.save()
            Vote.objects.filter(room=room).delete()


class PauseSongView(APIView):
    def put(self, response, format=None):
        room_code = self.request.session.get("room_code")
        room = Room.objects.filter(code=room_code)
        if room.exists():
            room = room[0]
        else:
            return Response({"Not Found": "You are not a host of any room"}, status=status.HTTP_404_NOT_FOUND)
        
        if self.request.session.session_key == room.host or room.guest_can_pause:
            pause_song(room.host)
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        return Response({"Error": "You have not permission to pause song"}, status=status.HTTP_403_FORBIDDEN)
    

class PlaySongView(APIView):
    def put(self, response, format=None):
        room_code = self.request.session.get("room_code")
        room = Room.objects.filter(code=room_code)
        if room.exists():
            room = room[0]
        else:
            return Response({"Not Found": "You are not a host of any room"}, status=status.HTTP_404_NOT_FOUND)
        
        if self.request.session.session_key == room.host or room.guest_can_pause:
            play_song(room.host)
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        return Response({"Error": "You have not permission to play song"}, status=status.HTTP_403_FORBIDDEN)
    

class NextSongView(APIView):
    def post(self, request, format=None):
        room_code = self.request.session.get("room_code")
        room = Room.objects.filter(code=room_code)
        if room.exists():
            room = room[0]
        else:
            return Response({"Not Found": "You are not a host of any room"}, status=status.HTTP_404_NOT_FOUND)
        
        votes = Vote.objects.filter(room=room, song_id=room.current_song)
        votes_needed = room.votes_to_skip

        if self.request.session.session_key == room.host or len(votes) + 1 >= votes_needed:
            votes.delete()
            next_song(room.host)
        else:
            vote = Vote()
            vote.user = self.request.session.session_key
            vote.room = room
            vote.song_id = room.current_song
            vote.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)