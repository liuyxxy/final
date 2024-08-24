from django.shortcuts import render, get_object_or_404
from .models import *

# Create your views here.
def home(request):
    return render(request, 'home.html')

def game(request):
    room = get_object_or_404(Room, room_id='703acb23-d420-4524-a053-03a1132b98ed')
    players = room.room_players.all()
    texts = room.room_texts.all()
    return render(request, 'game.html', {'room': room, 'players': players, 'texts': texts})