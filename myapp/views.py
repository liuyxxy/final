import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from .models import *
from .forms import CreateHostForm, CreatePlayerForm, CreateSentenceForm

# Create your views here.
def home(request):
    return render(request, 'home.html')

def create(request): 
        # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = CreateHostForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            hostname = form.cleaned_data['hostname']
            num_rounds = form.cleaned_data['num_rounds']
            time = form.cleaned_data['time']
            
            room = Room(time_limit=time, rounds=num_rounds)
            host = Player(user=hostname, room=room)
            room.host = host
            room.save()
            host.save()
            request.session['room_id'] = str(room.room_id)
            # redirect to a new URL:
            return redirect(wait)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = CreateHostForm()

    return render(request, 'create.html', {'form': form})

def wait(request):
    # if host, can view link, who is in room and start game. 
    # if player, can view link and who is in room.
    # only host has post method
    room = get_object_or_404(Room, room_id=request.session['room_id'])
    players = room.room_players.all()
    return render(request, 'wait.html', {'players': players})

def join(request):
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = CreatePlayerForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            playername = form.cleaned_data['playername']
            room = get_object_or_404(Room, room_id=request.session['room_id'])
            player = Player(user=playername, room=room)
            player.save()
            # redirect to a new URL:
            return redirect(wait)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = CreatePlayerForm()
    return render(request, 'join.html', {'form': form})

def game(request):
    room = get_object_or_404(Room, room_id=request.session['room_id'])
    players = room.room_players.all()
    texts = room.room_texts.all()
    if request.method == "POST":
                # create a form instance and populate it with data from the request:
        form = CreateSentenceForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            body = form.cleaned_data['body']
            room = get_object_or_404(Room, room_id=request.session['room_id'])
            sentence = Sentence(room=room, content=body)
            sentence.save()
    else:
        form = CreateSentenceForm()
    return render(request, 'game.html', {'room': room, 'players': players, 'texts': texts, 'form':form})