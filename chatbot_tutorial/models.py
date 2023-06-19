from django.contrib.auth.models import User
from django.db import models
from enum import Enum


class JokeTypes(Enum):
    FAT = "Fat"
    DUMB = "Dumb"
    STUPID = "Stupid"


class TelegramUser(models.Model):
    id = models.IntegerField(primary_key=True)
    first_name = models.CharField(default="Unkown", max_length=50)
    last_name = models.CharField(default="Name", max_length=50)


class JokeRequest(models.Model):
    JOKETYPES = (
        (JokeTypes.FAT.name, "fat"),
        (JokeTypes.DUMB.name, "dumb"),
        (JokeTypes.STUPID.name, "stupid"),
    )
    telegram_user = models.ForeignKey(
        TelegramUser, on_delete=models.CASCADE, related_name="telegramuser"
    )
    joke_type = models.CharField(max_length=10, choices=JOKETYPES)
