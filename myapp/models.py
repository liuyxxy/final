from django.db import models
import uuid

# Create your models here.
class Room(models.Model):
    room_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    host = models.CharField(default='', max_length=50)
    time_limit = models.IntegerField(choices=[(10, '10s'), (20, '20s'), (30, '30s'), (40, '40s')], default=20)
    rounds = models.PositiveIntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Room {self.room_id} hosted by {self.host}"
    
class Player(models.Model):
    room = models.ForeignKey(Room, related_name="room_players", on_delete=models.CASCADE)
    user = models.CharField(max_length=50)
    score = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user} in Room {self.room.room_id}"

class Sentence(models.Model):
    room = models.ForeignKey(Room, related_name="room_texts", on_delete=models.CASCADE)
    player = models.ForeignKey(Player, related_name="player_texts", on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Sentence by {self.player.user} in {self.room.room_id}"
