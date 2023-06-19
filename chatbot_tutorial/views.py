from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http.response import HttpResponse
from django.shortcuts import render
from django.db.models import Count, Q
import json
import requests
import random
import traceback
from .settings import TELEGRAM_TOKEN
from .models import TelegramUser, JokeRequest, JokeTypes

TELEGRAM_BOT_URL = "https://api.telegram.org/bot{0}/sendMessage".format(TELEGRAM_TOKEN)
GREETING_TEXT = "Hello there! If you're interested in yo mama jokes, just tell me fat, stupid or dumb and i'll tell you an appropriate joke."
I_DONT_KNOW_TEXT = "I don't know any responses for that. I can only tell yo mama jokes."


def chat(request):
    context = {}
    return render(request, "chatbot_tutorial/chatbot.html", context)


def get_reply(text_from_user: str):
    text_from_user = text_from_user.lower()
    jokes = {
        "stupid": [
            """Yo' Mama is so stupid, she needs a recipe to make ice cubes.""",
            """Yo' Mama is so stupid, she thinks DNA is the National Dyslexics Association.""",
        ],
        "fat": [
            """Yo' Mama is so fat, when she goes to a restaurant, instead of a menu, she gets an estimate.""",
            """ Yo' Mama is so fat, when the cops see her on a street corner, they yell, "Hey you guys, break it up!" """,
        ],
        "dumb": [
            """Yo' Mama is so dumb, when God was giving out brains, she thought they were milkshakes and asked for extra thick.""",
            """Yo' Mama is so dumb, she locked her keys inside her motorcycle.""",
        ],
    }

    reply = ""
    msg_is_joke_req = False
    if "fat" in text_from_user:
        reply = random.choice(jokes["fat"])
        msg_is_joke_req = True

    elif "stupid" in text_from_user:
        reply = random.choice(jokes["stupid"])
        msg_is_joke_req = True

    elif "dumb" in text_from_user:
        reply = random.choice(jokes["dumb"])
        msg_is_joke_req = True

    elif "/start" == text_from_user:
        reply = "Hello there!!"

    elif text_from_user in ["hi", "hey", "hello"]:
        reply = GREETING_TEXT
    else:
        reply = I_DONT_KNOW_TEXT

    return reply, msg_is_joke_req


def respond_to_websockets(message):
    result_message = {"type": "text"}
    reply, _ = get_reply(message["text"])
    result_message["text"] = reply
    return result_message


def get_or_create_user(user: dict):
    t_user, created = TelegramUser.objects.get_or_create(id=user["id"])
    if created:
        t_user.first_name = user["first_name"]
        t_user.last_name = user["last_name"]
        t_user.save()
    return t_user


def get_stats(request):
    joke_type_queries = {
        "fat_joke_count": Count("id", filter=Q(joke_type="Fat")),
        "dumb_joke_count": Count("id", filter=Q(joke_type="Dumb")),
        "stupid_joke_count": Count("id", filter=Q(joke_type="Stupid")),
    }
    requests = (
        JokeRequest.objects.values("telegram_user")
        .annotate(**joke_type_queries)
        .values(
            "telegram_user__id",
            "telegram_user__first_name",
            "fat_joke_count",
            "dumb_joke_count",
            "stupid_joke_count",
        )
    )
    joke_type_stats = (
        JokeRequest.objects.values("joke_type")
        .annotate(req_count=Count("joke_type"))
        .values("joke_type", "req_count")
        .all()
    )
    joke_type_stats = list(joke_type_stats)
    return render(
        request,
        "chatbot_tutorial/stats.html",
        {"requests": requests, "joke_type_stats": joke_type_stats},
    )


def save_joke_request(user, joke_type):
    joke_req = JokeRequest(telegram_user=user, joke_type=joke_type)
    joke_req.save()


class TelegramBotView(generic.View):
    default_res_keyboard = {
        "inline_keyboard": [
            [{"text": jokeType.value, "callback_data": jokeType.value}]
            for jokeType in JokeTypes
        ]
    }

    button_response = {
        "text": "Tell me fat, stupid or dumb and I'll tell you an appropriate joke.",
        "reply_markup": default_res_keyboard,
    }

    # csrf_exempt is necessary because the request comes from the Telegram server.
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    @staticmethod
    def get_message_from_request(request):
        received_message = {}
        decoded_request = json.loads(request.body.decode("utf-8"))

        if "callback_query" in decoded_request:
            received_message = decoded_request["callback_query"]
        elif "message" in decoded_request:
            received_message = decoded_request["message"]
        else:
            return {}
        received_message["from_user_id"] = received_message["from"][
            "id"
        ]  # simply for easier reference

        return received_message

    @staticmethod
    def post_to_telegram_bot(response: dict):
        response_msg = json.dumps(response)
        requests.post(
            TELEGRAM_BOT_URL,
            headers={"Content-Type": "application/json"},
            data=response_msg,
        )

    @staticmethod
    def get_user_input(message: dict):
        if "data" in message.keys():
            return message["data"]
        return message["text"]

    @staticmethod
    def send_message_to_telegram_bot(message):
        msg_from_bot = TelegramBotView.get_user_input(message)
        if msg_from_bot:
            reply, _ = get_reply(msg_from_bot)
        else:
            reply = I_DONT_KNOW_TEXT
        chat_id = message.get("from_user_id")
        response = {}
        response["chat_id"] = chat_id
        response["text"] = reply
        TelegramBotView.post_to_telegram_bot(response)
        btn_res_with_chat_id = {
            **TelegramBotView.button_response,
            "chat_id": chat_id,
        }
        TelegramBotView.post_to_telegram_bot(btn_res_with_chat_id)

    @staticmethod
    def save_message_request(message):
        user = get_or_create_user(message["from"])
        msg_from_bot = TelegramBotView.get_user_input(message)
        if not msg_from_bot:
            return
        _, msg_is_joke_req = get_reply(msg_from_bot)
        if msg_is_joke_req:
            save_joke_request(user, msg_from_bot)

    def post(self, request, *args, **kwargs):
        try:
            message = self.get_message_from_request(request)
            TelegramBotView.save_message_request(message)
            self.send_message_to_telegram_bot(message)
        except Exception as e:
            print(traceback.format_exc())
        return HttpResponse()
