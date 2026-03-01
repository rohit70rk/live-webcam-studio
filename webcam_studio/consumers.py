import json
from channels.generic.websocket import AsyncWebsocketConsumer

class SignalingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'stream_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        
        # Broadcast the message to everyone in the room EXCEPT the sender
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'signaling_message',
                'message': data,
                'sender': self.channel_name
            }
        )

    async def signaling_message(self, event):
        message = event['message']
        sender = event['sender']

        # Send message to WebSocket if it's not from us
        if sender != self.channel_name:
            await self.send(text_data=json.dumps(message))