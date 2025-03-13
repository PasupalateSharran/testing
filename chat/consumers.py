import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .utils import assign_superhero_name

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "chat_anonymous"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        self.username = assign_superhero_name()
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        message = json.loads(text_data)['message']
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': f"{self.username}: {message}"
            }
        )

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({'message': message}))
