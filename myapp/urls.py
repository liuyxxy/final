from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create_room/', views.create_room, name='create_room'),
    path('api/start-game/', views.start_game, name='start_game'),
    path('room/<uuid:room_id>/', views.room_detail, name='room_detail'),
]