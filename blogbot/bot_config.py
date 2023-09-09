import os

import aiogram
import redis.asyncio as redis
from dotenv import load_dotenv

load_dotenv()

# url
basic_url = 'http://127.0.0.1:8000/api/'
# bot
bot = aiogram.Bot(token=str(os.getenv('BOT_KEY')))
dp = aiogram.Dispatcher()

# redis
redis_client = redis.Redis(host=str(os.getenv('REDIS_HOST')), port=int(os.getenv('REDIS_PORT')), db=0,
                           decode_responses=True)
