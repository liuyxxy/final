import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Room, Player, Sentence
from django.utils import timezone
from asgiref.sync import sync_to_async
import random

class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'room_{self.room_id}'

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Notify others that a new player has joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'player_joined',
                'message': f'A new player has joined the room.'
            }
        )

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Optionally notify others that a player has left
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'player_left',
                'message': f'A player has left the room.'
            }
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'start_game':
            await self.start_game()
        elif action == 'submit_sentence':
            username = data.get('username')
            text = data.get('text')
            await self.submit_sentence(username, text)
        # Handle other actions as needed

    # Send message to WebSocket
    async def send_message(self, message):
        await self.send(text_data=json.dumps({
            'message': message
        }))

    # Event handler for player joined
    async def player_joined(self, event):
        await self.send(text_data=json.dumps({
            'event': 'player_joined',
            'message': event['message']
        }))

    # Event handler for player left
    async def player_left(self, event):
        await self.send(text_data=json.dumps({
            'event': 'player_left',
            'message': event['message']
        }))

    # Start game logic
    async def start_game(self):
        room = await sync_to_async(get_object_or_404)(Room, id=self.room_id)
        if room.status != 'waiting':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send_message',
                    'message': 'Game has already started.'
                }
            )
            return

        room.status = 'in_progress'
        await sync_to_async(room.save)()

        # Shuffle players to randomize order
        players = list(room.players.all())
        random.shuffle(players)
        room.players_order = [player.id for player in players]
        await sync_to_async(room.save)()

        # Assign the first player
        room.current_player = players[0]
        await sync_to_async(room.save)()

        # Notify all players that the game has started
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_started',
                'current_player': room.current_player.username
            }
        )

    # Event handler for game started
    async def game_started(self, event):
        await self.send(text_data=json.dumps({
            'event': 'game_started',
            'current_player': event['current_player']
        }))

    # Submit sentence logic
    async def submit_sentence(self, username, text):
        room = await sync_to_async(get_object_or_404)(Room, id=self.room_id)
        player = await sync_to_async(get_object_or_404)(Player, username=username, room=room)

        # Determine current round
        current_round = room.current_round

        # Save the sentence
        await sync_to_async(Sentence.objects.create)(
            player=player,
            room=room,
            round_number=current_round,
            text=text,
            submitted_at=timezone.now()
        )

        # Determine next player
        players = list(room.players.all())
        current_index = players.index(room.current_player)
        next_index = (current_index + 1) % len(players)
        next_player = players[next_index]

        # Update current player
        room.current_player = next_player
        await sync_to_async(room.save)()

        # Notify all players about the next turn
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'next_turn',
                'current_player': next_player.username
            }
        )

    # Event handler for next turn
    async def next_turn(self, event):
        await self.send(text_data=json.dumps({
            'event': 'next_turn',
            'current_player': event['current_player']
        }))
        
    async def check_game_completion(self):
        room = await sync_to_async(get_object_or_404)(Room, id=self.room_id)
        total_sentences = Sentence.objects.filter(room=room, round_number__lte=room.total_rounds).count()
        expected_sentences = room.total_rounds * room.players.count()
        
        if total_sentences >= expected_sentences:
            # Game is complete
            room.status = 'finished'
            await sync_to_async(room.save)()

            # Compile all sentences
            sentences = await sync_to_async(list)(room.sentences.order_by('round_number'))
            paragraph = ' '.join([s.text for s in sentences])

            # Calculate word counts
            word_counts = {}
            for s in sentences:
                word_counts[s.player.username] = word_counts.get(s.player.username, 0) + len(s.text.split())

            # Identify players with most and least words
            if word_counts:
                max_words = max(word_counts.values())
                min_words = min(word_counts.values())
                most_words_player = [user for user, count in word_counts.items() if count == max_words]
                least_words_player = [user for user, count in word_counts.items() if count == min_words]
            else:
                most_words_player = []
                least_words_player = []

            # Notify all players
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_completed',
                    'paragraph': paragraph,
                    'most_words_player': most_words_player,
                    'least_words_player': least_words_player
                }
            )

    async def game_completed(self, event):
        await self.send(text_data=json.dumps({
            'event': 'game_completed',
            'paragraph': event['paragraph'],
            'most_words_player': event['most_words_player'],
            'least_words_player': event['least_words_player'],
        }))