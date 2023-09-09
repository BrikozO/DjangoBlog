import asyncio

from aiogram import F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, InlineKeyboardButton, KeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiohttp import ClientSession

from bot_config import dp, redis_client, bot, basic_url


def is_authorised(ignore_auth: bool = False):
    def auth_decorator_logic(func):
        async def wrapper(*args, **kwargs):
            user_token = await redis_client.get(args[0].from_user.id)
            if not ignore_auth:
                if user_token is not None:
                    return await func(*args)
                else:
                    await bot.send_message(args[0].chat.id, 'Для работы с ботом блога вам необходимо авторизоваться!')
            else:
                if func.__name__ == 'auth_user' and user_token:
                    await bot.send_message(args[0].chat.id, 'Вы уже авторизованы!')
                else:
                    return await func(command=kwargs.get('command'), *args)

        return wrapper

    return auth_decorator_logic


# json data
async def get_json(token: str = None):
    params = {'Authorization': 'Token ' + token, }
    async with ClientSession(headers=params) as session:
        async with session.get(url=basic_url) as response:
            data = await response.json()
            return data


@dp.message(Command(commands=["start"]))
async def process_start_command(message: Message):
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text='Ссылка на сайт'),
                KeyboardButton(text='Ссылка на github'))
    await message.answer(
        'Привет! Спасибо, что используете brikologot! Для того, чтобы узнать о функционале бота, введите: /help',
        reply_markup=builder.as_markup(resize_keyboard=True))


@dp.message(Command(commands=['help']))
async def process_help_command(message: Message):
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
    await message.answer(text=text, parse_mode='MarkdownV2')


@dp.message(Command(commands=['logout']))
@is_authorised()
async def logout(message: Message):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='Да', callback_data='logout_accepted'))
    builder.add(InlineKeyboardButton(text='Нет', callback_data='logout_rejected'))
    await message.answer('Вы уверены что хотите выйти?', reply_markup=builder.as_markup())


@dp.callback_query(F.data == 'logout_accepted')
async def logout_accepted(callback: CallbackQuery):
    await redis_client.delete(callback.from_user.id)
    await callback.message.answer('Вы вышли из системы!')


@dp.callback_query(F.data == 'logout_rejected')
async def logout_rejected(callback: CallbackQuery):
    await callback.message.answer('Хорошо. Продолжайте работу с ботом!')


@dp.message(Command(commands=['auth']))
@is_authorised(ignore_auth=True)
async def auth_user(message: Message, command: CommandObject):
    if command.args:
        try:
            username, password = command.args.split()
            async with ClientSession() as session:
                user_info = {'username': username, 'password': password}
                async with session.post(url=basic_url + 'api-token-auth/', data=user_info) as response:
                    data = await response.json()
                    if data.get('token') is not None:
                        await redis_client.set(name=message.from_user.id, value=data.get('token') + '|' + f'{username}')
                        await message.answer('Вы успешно авторизованы!')
                    else:
                        await message.answer('Неверные имя пользователя или пароль!')
        except:
            await message.answer('Ошибка: некорректно введенные данные!')
    else:
        await message.answer('Введите логин и пароль через пробел после команды!')


@dp.message(Command(commands=['post_list']))
@is_authorised()
async def post_list(message: Message):
    builder = InlineKeyboardBuilder()
    token = await redis_client.get(message.from_user.id)
    data = await get_json(token=token.split('|')[0])
    for item in data['results']:
        url = basic_url + str(int(item['id']))
        builder.add(InlineKeyboardButton(text=item['title'], url=url))
    builder.adjust(3)
    await message.answer(text='Выберите пост', reply_markup=builder.as_markup())


async def main():
    await dp.start_polling(bot)
    await asyncio.create_task(get_json())


if __name__ == '__main__':
    asyncio.run(main())
