import os

import redis
import requests
import telebot
from dotenv import load_dotenv
from telebot import types

load_dotenv()

with redis.Redis(host=str(os.getenv('REDIS_HOST')), port=int(os.getenv('REDIS_PORT')), db=0) as redis_client:
    bot = telebot.TeleBot(str(os.getenv('BOT_KEY')))

    response = requests.get('http://127.0.0.1:8000/api/')


    def is_authorised(ignore_auth: bool = False):
        def auth_decorator_logic(func):
            def wrapper(*args, **kwargs):
                user_token = redis_client.get(args[0].from_user.id)
                if not ignore_auth:
                    if user_token is not None:
                        return func(*args, **kwargs)
                    else:
                        bot.send_message(args[0].chat.id, 'Для работы с ботом блога вам необходимо авторизоваться!')
                else:
                    if func.__name__ == 'auth_user' and user_token:
                        bot.send_message(args[0].chat.id, 'Вы уже авторизованы!')
                    else:
                        return func(*args, **kwargs)

            return wrapper

        return auth_decorator_logic


    def get_user_name(user_id):
        return redis_client.get(user_id).decode('UTF-8').split('|')[1]


    @bot.message_handler(commands=['start'])
    @is_authorised(ignore_auth=True)
    def start(message):
        bot.send_message(message.chat.id,
                         'Привет! Спасибо, что используете brikologot! Для того, чтобы узнать о функционале бота, введите: /help')


    @bot.message_handler(commands=['help'])
    @is_authorised(ignore_auth=True)
    def help(message):
        text = (
            '`Здравствуйте! Вы пользуеетесь ботом` Brikologot`, созданным `*brikoz*` для тестирования API своего блога.\n'
            'Если вы хотите получить доступ к сайту, перейдите по ссылке:` http://127\\.0\\.0\\.1:8000\n'
            '`Однако, вы можете протестировать и фукнциональность бота, которая постоянно расширяется! '
            'На данный момент вам доступно` 5 команд`:\n'
            '/start - начало работы\n'
            '/help - список команд и краткий экскурс\n'
            '/auth - авторизация\n'
            '/logout - выход из системы\n'
            '/post_list - список опубликованных постов блога\n'
            'Приятного использования!`')

        bot.send_message(message.chat.id, text, parse_mode='MarkdownV2')


    @bot.message_handler(commands=['post_list'])
    @is_authorised()
    def post_list(message):
        markup = types.InlineKeyboardMarkup()
        for item in response.json().get('results'):
            url = 'http://127.0.0.1:8000/api/' + str(item['id'])
            markup.add(types.InlineKeyboardButton(item['title'], url=url))
        bot.send_message(message.from_user.id, 'Выберите пост', reply_markup=markup)


    @bot.message_handler(commands=['auth'])
    @is_authorised(ignore_auth=True)
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
            redis_client.set(name=message.from_user.id, value=sign_try.json().get('token') + '|' + f'{login}')
            bot.send_message(message.chat.id, 'Вы успешно авторизованы!')
        else:
            bot.send_message(message.chat.id, 'Неверный логин или пароль!')


    @bot.message_handler(commands=['logout'])
    @is_authorised()
    def logout(message):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Да', callback_data='logout_true'))
        markup.add(types.InlineKeyboardButton('Нет', callback_data='logout_false'))
        bot.reply_to(message, 'Вы уверены, что хотите выйти?', reply_markup=markup)


    @bot.callback_query_handler(func=lambda call: True)
    def callback(call):
        if call.message:
            if call.data == 'logout_true':
                redis_client.delete(call.from_user.id)
                bot.send_message(call.message.chat.id, 'Вы вышли из системы!')
            else:
                username = get_user_name(call.from_user.id)
                bot.send_message(call.message.chat.id, f'Хорошо, {username}. Продолжайте работу с ботом!')


    bot.polling()
