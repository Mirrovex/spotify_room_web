from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import generics, status
from api.models import Room
from api.serializers import RoomSerializer, CreateRoomSerializer, UpdateRoomSerializer, UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from spotify.models import SpotifyToken
from api.models import Room

def main(request):
    return HttpResponse("<h1>Hello World</h1>")


class ResetView(APIView):
    def get(self, request, format=None):
        request.session.flush()

        Room.objects.all().delete()
        SpotifyToken.objects.all().delete()

        return Response({"Message": "Reset succesfull"}, status=status.HTTP_200_OK)


class RoomView(generics.ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


class UserView(generics.ListAPIView):
    queryset = SpotifyToken.objects.all()
    serializer_class = UserSerializer
        

class GetRoom(APIView):
    serializer_class = RoomSerializer
    lookup_url_kwarg = "code"

    def get(self, request, format=None):
        code = request.GET.get(self.lookup_url_kwarg)
        if code != None:
            room = Room.objects.filter(code=code)
            if room.exists():
                data = RoomSerializer(room[0]).data
                data["is_host"] = self.request.session.session_key == room[0].host
                return Response(data, status=status.HTTP_200_OK)
            return Response({"Room Not Found": "Invalid Room Code"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"Bad Request": "Code parameter not found in request"}, status=status.HTTP_400_BAD_REQUEST)


class UserInRoomView(APIView):
    def get(self, request, format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        data = {
            "code": self.request.session.get("room_code")
        }
        return JsonResponse(data, status=status.HTTP_200_OK)
    

class LeaveRoomView(APIView):
    def post(self, request, format=None):
        if "room_code" in self.request.session:
            self.request.session.get("room_code")
            host_id = self.request.session.session_key

            room_result = Room.objects.filter(host=host_id)
            print(room_result)
            if room_result.exists():
                room = room_result[0]
                room.delete()

        return Response({"Message": "Success"}, status=status.HTTP_200_OK)


class CreateRoomView(APIView):
    serializer_class = CreateRoomSerializer

    def post(self, request, format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            guest_can_pause = serializer.data.get("guest_can_pause")
            votes_to_skip = serializer.data.get("votes_to_skip")
            host = self.request.session.session_key
            queryset = Room.objects.filter(host=host)

            if queryset.exists():
                room = queryset[0]
                room.guest_can_pause = guest_can_pause
                room.votes_to_skip = votes_to_skip
                # room.save(update_fields=['guest_can_pause', 'votes_to_skip'])
                room.save()
                self.request.session["room_code"] = room.code
                return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)
            else:
                room = Room()
                room.host = host
                room.guest_can_pause = guest_can_pause
                room.votes_to_skip = votes_to_skip
                room.save()
                self.request.session["room_code"] = room.code
                return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)


class JoinRoomView(APIView):
    lookup_url_kwarg = "code"

    def post(self, request, format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        code = request.data.get(self.lookup_url_kwarg)
        if code != None:
            room = Room.objects.filter(code=code)
            if room.exists():
                room = room[0]
                self.request.session["room_code"] = code
                return Response({"Message": "Room Joined!"}, status=status.HTTP_200_OK)
            return Response({"Bad Request": "Invalid Room Code"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"Bad Request": "Invalid post data, room with this code not found"}, status=status.HTTP_400_BAD_REQUEST)
    

class UpdateRoomView(APIView):
    serializer_class = UpdateRoomSerializer

    def patch(self, request, format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            guest_can_pause = serializer.data.get("guest_can_pause")
            votes_to_skip = serializer.data.get("votes_to_skip")
            code = serializer.data.get("code")

            queryset = Room.objects.filter(code=code)
            if queryset.exists():
                room = queryset[0]
                user_id = self.request.session.session_key
                if room.host == user_id:
                    room.guest_can_pause = guest_can_pause
                    room.votes_to_skip = votes_to_skip
                    room.save()
                    return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)
                return Response({"Message": "You are not the host of this room"}, status=status.HTTP_403_FORBIDDEN)
            return Response({"Bad Request": "Room not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"Bad Request": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)