from django.db import models
import uuid

# Create your models here.

class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    host = models.ForeignKey('Player', related_name='hosted_rooms', on_delete=models.CASCADE)
    time_per_round = models.PositiveIntegerField(choices=[(10, '10s'), (20, '20s'), (30, '30s'), (40, '40s')])
    total_rounds = models.PositiveIntegerField()
    current_round = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=[('waiting', 'Waiting'), ('in_progress', 'In Progress'), ('finished', 'Finished')], default='waiting')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Room {self.id} hosted by {self.host.username}"

class Player(models.Model):
    username = models.CharField(max_length=150)
    room = models.ForeignKey(Room, related_name='players', on_delete=models.CASCADE)
    is_host = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('username', 'room')

    def __str__(self):
        return self.username

class Sentence(models.Model):
    player = models.ForeignKey(Player, related_name='sentences', on_delete=models.CASCADE)
    room = models.ForeignKey(Room, related_name='sentences', on_delete=models.CASCADE)
    round_number = models.PositiveIntegerField()
    text = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Round {self.round_number} by {self.player.username}"