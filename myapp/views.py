# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError, transaction

def home(request):
    return render(request, 'home.html')

def create_room(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        time_per_round = int(request.POST.get('time'))
        total_rounds = int(request.POST.get('rounds'))
        
        try:
            # Start a transaction
            with transaction.atomic():
                # Create a temporary Room instance without a host
                room = Room.objects.create(
                    time_per_round=time_per_round,
                    total_rounds=total_rounds
                )

                # Create the Player instance (who will be the host)
                host_player = Player.objects.create(room=room, username=username, is_host=True)

                # Assign the host to the room and save the room again
                room.host = host_player
                room.save()

            # Redirect to the room detail page
            return redirect('room_detail', room_id=room.id)
        
        except IntegrityError:
            # Handle the error (e.g., show an error message to the user)
            return render(request, 'create_room.html', {'error': 'An error occurred while creating the room.'})

    else:
        return render(request, 'create_room.html')

def room_detail(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    if request.method == 'POST':
        username = request.POST.get('username')

        # Check for unique username within the room
        if Player.objects.filter(username=username, room=room).exists():
            messages.error(request, "Username already taken in this room. Please choose another.")
            return redirect('room_detail', room_id=room.id)
        else:
            # Create a new Player
            player = Player.objects.create(username=username, room=room)

            # Redirect to the game interface (could be the same page with different context)
            return redirect('game_interface', room_id=room.id, player_id=player.id)

    players = room.players.all()
    return render(request, 'room_detail.html', {'room': room, 'players': players})

@csrf_exempt
def start_game(request):
    if request.method == 'POST':
        room_id = request.POST.get('room_id')
        room = Room.objects.get(id=room_id)
        if room:
            room.has_started = True  # Assuming you have a `has_started` field in your Room model
            room.save()
            return JsonResponse({'status': 'success', 'message': 'Game started!'})
        return JsonResponse({'status': 'error', 'message': 'Room not found'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)