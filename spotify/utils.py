from django.utils import timezone
from datetime import timedelta
from requests import post, put, get

from spotify.models import SpotifyToken
from spotify.credentials import CLIENT_ID, CLIENT_SECRET

BASE_URL = "https://api.spotify.com/v1/me/"

def get_user_tokens(session_key):
    user_tokens = SpotifyToken.objects.filter(user=session_key)
    if user_tokens.exists():
        return user_tokens[0]
    return None


def update_or_create_user_tokens(session_key, access_token, token_type, expires_in, refresh_token):
    tokens = get_user_tokens(session_key)
    expires_in = timezone.now() + timedelta(seconds=expires_in)

    if not tokens:
        tokens = SpotifyToken()

    tokens.user = session_key
    tokens.access_token = access_token
    tokens.refresh_token = refresh_token
    tokens.expires_in = expires_in
    tokens.token_type = token_type
    tokens.save()


def is_spotify_auth(session_key):
    tokens = get_user_tokens(session_key)
    if tokens:
        expiry = tokens.expires_in
        if expiry <= timezone.now():
            refresh_spotify_token(session_key)
            
        return True
    return False


def refresh_spotify_token(session_key):
    refresh_token = get_user_tokens(session_key).refresh_token

    response = post("https://accounts.spotify.com/api/token", data={
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }).json()

    access_token = response.get("access_token")
    token_type = response.get("token_type")
    expires_in = response.get("expires_in")

    update_or_create_user_tokens(session_key, access_token, token_type, expires_in, refresh_token)


def execute_spotify_api_request(session_key, endpoint, post_=False, put_=False):
    tokens = get_user_tokens(session_key)
    headers = {"Authorization": f"Bearer {tokens.access_token}"}

    if post_:
        post(BASE_URL + endpoint, headers=headers)
    if put_:
        put(BASE_URL + endpoint, headers=headers)

    response = get(BASE_URL + endpoint, headers=headers)
    try:
        return response.json()
    except:
        return {"Error": "Issue with request", "status": response.status_code}
    

def pause_song(session_key):
    return execute_spotify_api_request(session_key, "player/pause", put_=True)

def play_song(session_key):
    return execute_spotify_api_request(session_key, "player/play", put_=True)

def next_song(session_key):
    return execute_spotify_api_request(session_key, "player/next", post_=True)