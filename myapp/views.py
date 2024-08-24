from django.shortcuts import render, get_object_or_404
from .models import *

# Create your views here.
def home(request):
    return render(request, 'home.html')

def game(request):
    room = get_object_or_404(Room, room_id='0a9f4e42-6e49-44b6-95f3-b1b876491038')
    players = room.room_players.all()
    texts = room.room_texts.all()
    return render(request, 'game.html', {'room': room, 'players': players, 'texts': texts})