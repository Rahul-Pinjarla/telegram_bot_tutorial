import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import chatbot_tutorial.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chatbot_tutorial.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": URLRouter(chatbot_tutorial.routing.websocket_urlpatterns),
    }
)
