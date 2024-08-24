import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from .models import *
from .forms import CreateForm

def getcookie(request):  
    tutorial  = request.COOKIES['java-tutorial']  
    return HttpResponse("java tutorials @: "+  tutorial); 

# Create your views here.
def home(request):
    return render(request, 'home.html')

def create(request):
        # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = CreateForm(request.POST)
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
            return redirect(game)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = CreateForm()

    return render(request, 'create.html', {'form': form})

def game(request):
    room = get_object_or_404(Room, room_id=request.session['room_id'])
    players = room.room_players.all()
    texts = room.room_texts.all()
    return render(request, 'game.html', {'room': room, 'players': players, 'texts': texts})