import telebot
import requests
from telebot import types
from dotenv import load_dotenv
import redis
import os

load_dotenv()

redis_client = redis.Redis(host=str(os.getenv('REDIS_HOST')), port=int(os.getenv('REDIS_PORT')), db=0)
bot = telebot.TeleBot(str(os.getenv('BOT_KEY')))

response = requests.get('http://127.0.0.1:8000/api/')


# headers={'Authorization': 'Token a8524338a789e0ae1d7cd13975f984b465a1a995'})


def get_auth_data(message):
    if redis_client.get(message.from_user.id) is not None:
        return True
    else:
        bot.send_message(message.chat.id, 'Для работы с ботом блога вам необходимо авторизоваться!')
        return False


@bot.message_handler(commands=['start'])
def start(message):
    if redis_client.get(message.from_user.id) is not None:
        msg = bot.send_message(message.chat.id, 'Привет! Вы авторизованы, поэтому можете пользоваться ботом!')
    else:
        msg = bot.send_message(message.chat.id, 'Привет! Для работы с ботом блога вам необходимо авторизоваться!')


@bot.message_handler(commands=['post_list'])
def post_list(message):
    if get_auth_data(message):
        markup = types.InlineKeyboardMarkup()
        for item in response.json().get('results'):
            url = 'http://127.0.0.1:8000/api/' + str(item['id'])
            markup.add(types.InlineKeyboardButton(item['title'], url=url))
        bot.send_message(message.from_user.id, 'Выберите пост', reply_markup=markup)


@bot.message_handler(commands=['auth'])
def auth_user(message):
    msg = bot.reply_to(message, 'Введите логин:')
    bot.register_next_step_handler(msg, signup_login)


def signup_login(message):
    login = message.text
    msg = bot.send_message(message.chat.id, 'Введите пароль:')
    bot.register_next_step_handler(msg, signup, login)


def signup(message, login):
    password = message.text
    sign_try = requests.post('http://127.0.0.1:8000/api/api-token-auth/',
                             data={'username': login, 'password': password})
    if sign_try.json().get('token') is not None:
        bot.send_message(message.chat.id, 'Вы успешно авторизованы!')
        redis_client.set(name=message.from_user.id, value=sign_try.json().get('token'))
    else:
        bot.send_message(message.chat.id, 'Неверный логин или пароль!')


@bot.message_handler(commands=['logout'])
def logout(message):
    if get_auth_data(message):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Да', callback_data='logout_true'))
        markup.add(types.InlineKeyboardButton('Нет', callback_data='logout_false'))
        bot.reply_to(message, 'Вы уверены, что хотите выйти?', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.message:
        if call.data == 'logout_true':
            redis_client.delete(call.message.from_user.id)
            bot.send_message(call.message.chat.id, 'Вы вышли из системы!')
        else:
            bot.send_message(call.message.chat.id, 'Хорошо. Продолжайте работу с ботом!')


redis_client.close()
bot.polling()
