# Generated by Django 4.2.2 on 2023-06-18 07:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="TelegramUser",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("first_name", models.CharField(default="Unkown", max_length=50)),
                ("last_name", models.CharField(default="Name", max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name="JokeRequest",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "joke_type",
                    models.CharField(
                        choices=[
                            ("FAT", "fat"),
                            ("DUMB", "dumb"),
                            ("STUPID", "stupid"),
                        ],
                        max_length=10,
                    ),
                ),
                (
                    "telegram_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="telegramuser",
                        to="chatbot_tutorial.telegramuser",
                    ),
                ),
            ],
        ),
    ]
