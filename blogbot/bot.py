import telebot
import requests
from telebot import types
from dotenv import load_dotenv
import os

load_dotenv()

bot = telebot.TeleBot(str(os.getenv('BOT_KEY')))

responce = requests.get('http://127.0.0.1:8000/api/',
                        headers={'Authorization': 'Token a8524338a789e0ae1d7cd13975f984b465a1a995'})


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет! Для работы с ботом блога вам необходимо авторизоваться!')


@bot.message_handler(commands=['post_list'])
def post_list(message):
    markup = types.InlineKeyboardMarkup()
    for item in responce.json().get('results'):
        url = 'http://127.0.0.1:8000/api/' + str(item['id'])
        markup.add(types.InlineKeyboardButton(item['title'], url=url))
    bot.send_message(message.from_user.id, 'Выберите пост', reply_markup=markup)


bot.infinity_polling()
