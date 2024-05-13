from rest_framework import serializers
from api.models import Room
from spotify.models import SpotifyToken

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ('id', 'code', 'host', 'guest_can_pause', 
                  'votes_to_skip', 'created_at')
        

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpotifyToken
        fields = ('id', 'user', 'created_at', 'refresh_token', 
                  'access_token', 'expires_in', 'token_type')


class CreateRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ('guest_can_pause', 'votes_to_skip')


class UpdateRoomSerializer(serializers.ModelSerializer):
    code = serializers.CharField(validators=[])

    class Meta:
        model = Room
        fields = ('guest_can_pause', 'votes_to_skip', 'code')