import os

import redis
import requests
import telebot
from dotenv import load_dotenv

load_dotenv()

#url
basic_url = 'http://127.0.0.1:8000/api/'
#bot
bot = telebot.TeleBot(str(os.getenv('BOT_KEY')))
#json data
response = requests.get(basic_url)
#redis
redis_client = redis.Redis(host=str(os.getenv('REDIS_HOST')), port=int(os.getenv('REDIS_PORT')), db=0)