from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('create/', views.create, name="create"),
    path('wait/', views.wait, name="wait"),
    path('join/', views.join, name="join"),
    path('game/', views.game, name="game")
]