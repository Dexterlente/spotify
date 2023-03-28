from django.urls import path
from .views import RoomAPIView


urlpatterns = [
    path('room', RoomAPIView.as_view(), name='room'),
    path('room/<str:code>', RoomAPIView.as_view(), name='room-detail'),
]