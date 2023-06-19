import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .views import respond_to_websockets, GREETING_TEXT


class ChatConsumer(WebsocketConsumer):
    rooms_length = 0

    def __int__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_name = None
        self.room_group_name = None
        self.room = None

    def connect(self):
        self.room_group_name = f"guest_chat{ChatConsumer.rooms_length}"

        self.accept()

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name,
        )

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "text": {
                    "type": "text",
                    "text": GREETING_TEXT,
                    "source": "BOT",
                },
                "type": "chat_message",
            },
        )

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name,
        )

    def receive(self, text_data=None):
        message = json.loads(text_data)
        self.chat_send(message)

    def chat_message(self, event):
        self.send(text_data=json.dumps(event))

    def chat_send(self, message):
        message_to_send_content = {
            "text": message["text"],
            "type": "text",
            "source": "CANDIDATE",
        }
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {"text": message_to_send_content, "type": "chat_message"},
        )
        response = respond_to_websockets(message)

        response["source"] = "BOT"
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"text": response, "type": "chat_message"}
        )
