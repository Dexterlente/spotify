from django.shortcuts import render

# Create your views here.
from rest_framework.generics import RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from .models import Room
from .serializers import RoomSerializer, CreateRoomSerializer, UpdateRoomSerializer


class RoomAPIView(RetrieveUpdateDestroyAPIView):
    lookup_field = 'code'
    serializer_class = RoomSerializer
    queryset = Room.objects.all()

    def get(self, request, *args, **kwargs):
        if 'code' in kwargs:
            room = Room.objects.filter(code=kwargs['code']).first()
            if room:
                data = self.serializer_class(room).data
                data['is_host'] = self.request.session.session_key == room.host
                return Response(data, status=status.HTTP_200_OK)
            return Response({'Room Not Found': 'Invalid Room Code.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'Bad Request': 'Code paramater not found in request'}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        serializer = CreateRoomSerializer(data=request.data)
        if serializer.is_valid():
            guest_can_pause = serializer.data.get('guest_can_pause')
            votes_to_skip = serializer.data.get('votes_to_skip')
            host = self.request.session.session_key
            queryset = Room.objects.filter(host=host)
            if queryset.exists():
                room = queryset.first()
                room.guest_can_pause = guest_can_pause
                room.votes_to_skip = votes_to_skip
                room.save(update_fields=['guest_can_pause', 'votes_to_skip'])
                self.request.session['room_code'] = room.code
                return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)
            else:
                room = Room(host=host, guest_can_pause=guest_can_pause, votes_to_skip=votes_to_skip)
                room.save()
                self.request.session['room_code'] = room.code
                return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)
        return Response({'Bad Request': 'Invalid data...'}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        code = kwargs['code']
        queryset = Room.objects.filter(code=code)
        if not queryset.exists():
            return Response({'msg': 'Room not found.'}, status=status.HTTP_404_NOT_FOUND)
        room = queryset.first()
        user_id = self.request.session.session_key
        if room.host != user_id:
            return Response({'msg': 'You are not the host of this room.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = UpdateRoomSerializer(data=request.data)
        if serializer.is_valid():
            guest_can_pause = serializer.data.get('guest_can_pause')
            votes_to_skip = serializer.data.get('votes_to_skip')
            room.guest_can_pause = guest_can_pause
            room.votes_to_skip = votes_to_skip
            room.save(update_fields=['guest_can_pause', 'votes_to_skip'])
            return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)
        return Response({'Bad Request': "Invalid Data..."}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        code = kwargs['code']
        queryset = Room.objects.filter(code=code)
        if not queryset.exists():
            return Response({'msg': 'Room not found.'}, status=status.HTTP_404_NOT_FOUND)
        room = queryset.first()
        user_id = self.request.session.session_key
    if room.host != user_id:
        return Response({'msg': 'You are not the host of this room.'}, status=status.HTTP_403_FORBIDDEN)
    room.delete()
    return Response({'msg': 'Room deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
