from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('create/', views.create, name="create"),
    # path('wait/<str:room_id>', views.wait, name="wait"),
    path('game/', views.game, name="game")
]