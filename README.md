# Intro

This is a simple bot that says yo-mama jokes (forked from vaisaghvt/django-bot-server-tutorial) . This project when set up successfully following the below instructions:
- can create a basic telegram bot using Django channels
- A websocket based bot which the user can interact with going to `http://localhot:8000/chat/` (this is also the default route)
- A stats page (`http://localhost:8000/stats/`) to show how may users used your bot and what calls they made, page also contains a graph on joke type/number of calls.

# Requirements
- Python3.9 (should also work with all python 3 versios)
- Make sure you have pip (pip --version)
- pip install virtualenv to install virtual environment
- Telegram messenger (you can also use the web version at web.telegram.org)

# First part

Fist part is to code and set up a bot server to connect to Telegram API via webhook and to respond to some messages with yo mama jokes.

## What to do

To get this running, you need the following. First install dependencies

### Step 0 : Clone the Repository

`git clone https://github.com/Rahul-Pinjarla/telegram_bot_tutorial.git`
`cd telegram_bot_tutorial`

### Step 1: Create virtualenv
`venv init .venv`
`source .venv/bin/activate`

### Step 2 : Install dependencies

`pip install -r requirements.txt`

### Step 3 : Run migrations 
`python manage.py makemigrations`
`python manage.py migrate`

### Step 4 : Start the local server

And start the server with 

`python manage.py runserver`

### Step 5 : Download and use ngrok

You need an HTTPS url for most webhooks for bots to work. For purely development purposes you can use ngrok. It gives a web-accessible HTTPS url that tunnels through to your localhost.
Download ngrok (https://ngrok.com/)  , got to a new tab on your terminal and start it with 

`ngrok http 8000`

At this point, you will have to add the URLs to ALLOWED_HOSTS in `chatbot_tutorial/settings.py`.

### Step 6 : Talk to the BotFather and get and set your bot token

Start telegram, and search for the Botfather. Talk to the Botfather on Telegram and give the command `/newbot` to create a bot and follow the instructions to get a token.

Copy the token and paste in `chatbot_tutorial/settings.py`

### Step 7 : Set your webhook by sending a post request to the Telegram API

If you are on a system where you can run a curl command, run the following command in your terminal (Remember to replace ngrok_url and bot_token)

`curl --location 'https://api.telegram.org/<bot_token>/setWebhook' \
--header 'Content-Type: application/json' \
--form 'url="https://<ngrok_url>/yo-mama-jokes/"'`

Alternatively, you can use some service like Postman or hurl.it just remember to do the following:

- Request type is "POST"
- url to post to https://api.telegram.org/bot<bot_token>/setWebhook
- as parameters add this (name, value) pair: (url, <ngrok_url>/yo-mama-jokes/)

You should get a response that states that "webhook has been set"

### Step 8 : Talk to the bot

You should now be able to talk to the bot , the bot will display 3 buttons, labelling 'Fat', 'Dumb' and 'Stupid' for the user to choose the joke they want.