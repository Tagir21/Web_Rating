
from django.shortcuts import render
from .models import Player

def home(request):
    return render(request, 'rating/home.html')

def rating_table(request):
    players = Player.objects.all().order_by('-rating')
    return render(request, 'rating/rating_table.html', {'players': players})