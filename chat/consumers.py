from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from django.core.files.storage import default_storage
from .models import Message, Chat, CustomUser
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'chat_{self.chat_id}'

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

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user = self.scope["user"]

        # Fetch the profile image URL
        profile_pic_url = await self.get_profile_image_url(user)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': user.username,
                'profile_pic_url': profile_pic_url,  # Include the profile picture URL in the event message
            }
        )

        # Save the message to the database
        await self.save_message(message, user)

    # Receive message from room group
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'profile_pic_url': event['profile_pic_url'],  # Send the profile picture URL to the client
        }))

    @database_sync_to_async
    def save_message(self, message, user):
        chat = Chat.objects.get(pk=self.chat_id)
        Message.objects.create(chat=chat, author=user, content=message)

    @database_sync_to_async
    def get_profile_image_url(self, user):
        if hasattr(user, 'freelancer_profile') and user.freelancer_profile.profile_image:
            return user.freelancer_profile.profile_image.url
        elif hasattr(user, 'client_profile') and user.client_profile.profile_image:
            return user.client_profile.profile_image.url
        else:
            # If there is no profile image, return the default image URL
            return default_storage.url('img/images.png')