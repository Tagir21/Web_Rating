from aiogram import Dispatcher, Bot, html, F, Router
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardMarkup, InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, FSInputFile

import os
import uuid
from mysql.connector import connect
from dotenv import dotenv_values
import asyncio

from db_init import add_bd_achievement, AchievementAddSchema

from admin import admin_r as admin_router


##########################################Добавить обработку когда несколько телеграммов к одному login в выбором да/нет ///ready
###########Добавить баны // ready
##########Добавить очистку из telegram_data по user_id = login

# Получение токена бота из переменной окружения .env
token = dotenv_values('.env')['BOT_TOKEN']
admin_id = dotenv_values('.env')['ADMIN_ID']

menu = Router()
add_achievement = Router()

async def save_file_to_disk(bot, file_id):
    file = await bot.get_file(file_id)
    ext = file.file_path.split('.')[-1] if '.' in file.file_path else 'bin'
    filename = f'{uuid.uuid4()}.{ext}'
    file_path = os.path.join('../../data', filename)

    print(file_path)
    await bot.download_file(file.file_path, destination=file_path)
    return file_path

def is_user_register(user_name: str):
    conn = connect(host='localhost',
                   port=3306,
                   username='root',
                   password='1234',
                   database='grades_db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, is_banned'
                   ' FROM telegram_data'
                   ' WHERE tg_name = %s', (user_name,))
    user_data = cursor.fetchone()
    conn.close()

    return user_data

def is_valid_login(login: str):
    conn = connect(host='localhost',
                   port=3306,
                   username='root',
                   password='1234',
                   database='grades_db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM users WHERE login = %s', (login,))
    user_id = cursor.fetchone()

    return user_id

def linked_telegrams(user_id: int):
    conn = connect(host='localhost',
                   port=3306,
                   username='root',
                   password='1234',
                   database='grades_db')
    cursor = conn.cursor()
    cursor.execute('SELECT tg_name'
                   ' FROM telegram_data'
                   ' WHERE user_id = %s', (user_id,))
    telegrams = cursor.fetchall()
    conn.close()

    return telegrams

def add_tg_user_name_in_db(tg_user_name: str, user_id: int):
    conn = connect(host='localhost',
                   port=3306,
                   username='root',
                   password='1234',
                   database='grades_db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO telegram_data (user_id, tg_name)'
                   ' VALUES'
                   ' (%s, %s)', (user_id, tg_user_name))
    conn.commit()
    conn.close()

class item_selection(StatesGroup):
    enter_login = State()
    confirm_linking = State()
    choosing = State()
    waiting_for_file = State()

@menu.message(Command('start', 'register'))
async def command_start_handler(message: Message, state: FSMContext):
    user_name = message.from_user.username
    tg_list = is_user_register(user_name)

    if tg_list:
        is_banned = tg_list[1]
        if is_banned:
            await message.answer('Вы были заблокированы администратором')
            return
        print(f'Я есть, но {tg_list}')
        await show_main_menu(message)
    else:
        print(f'Меня нет, но {tg_list}')
        await state.set_state(item_selection.enter_login)
        await message.answer(
            'Для начала работы введите ваш логин из академика',
            reply_markup=ReplyKeyboardRemove()
        )

@menu.message(item_selection.enter_login, F.text)
async def process_login(message: Message, state: FSMContext):
    login = message.text.strip()
    user_fetch = is_valid_login(login)
    if not user_fetch:
        await message.answer('Данного логина не существует, попробуйте ещё раз')
        return

    user_id = user_fetch[0]
    real_name = user_fetch[1]

    telegrams = linked_telegrams(user_id)
    if len(telegrams) > 0:
        await state.update_data(user_id=user_id, real_name=real_name)
        await state.set_state(item_selection.confirm_linking)
        telegram_list = '\n '.join([f'@{tg[0]}' for tg in telegrams])

        builder = InlineKeyboardBuilder()
        builder.button(text='Да', callback_data='confirm_linking')
        builder.button(text='Нет', callback_data='disconfirm_linking')

        await message.answer(f'К данному логину уже привязаны: {telegram_list}\n\n'
                             f'Вы уверены, что хотите продолжить?',
                             reply_markup=builder.as_markup(resize_keyboard=True))
        return

    await finish_linking(message, user_id, real_name, state)

@menu.callback_query(item_selection.confirm_linking, F.data == 'confirm_linking')
async def confirm_linking(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = data['user_id']
    real_name = data['real_name']
    tg_username = callback.from_user.username

    await finish_linking(callback, tg_username, user_id, real_name, state)
    await callback.answer()

@menu.callback_query(item_selection.confirm_linking, F.data == 'disconfirm_linking')
async def disconfirm_linking(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer('Привязка отменена\nВы можете начать заново с /start')

    await callback.answer()

async def finish_linking(source, tg_username:str, user_id: int, real_name: str,
                         state: FSMContext):
    add_tg_user_name_in_db(tg_username, user_id)
    await state.clear()
    if isinstance(source, CallbackQuery):
        await source.message.answer(f'Добро пожаловать, {real_name}!')
        await show_main_menu(source.message)
    else:
        await source.answer(f'Добро пожаловать, {real_name}!')
        await show_main_menu(source.message)

async def show_main_menu(message: Message):
    builder = ReplyKeyboardBuilder()
    builder.button(text='Добавить достижение')
    builder.button(text='Помощь')
    builder.button(text='Другое')
    builder.adjust(2)
    await message.answer(f'Выберите желаемое действие',
                         reply_markup=builder.as_markup(resize_keyboard=True))


@add_achievement.message(F.text == 'Добавить достижение')
async def add_button(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(item_selection.choosing)
    await state.update_data(items=[])

    builder = InlineKeyboardBuilder()
    builder.button(text='Учебная активность', callback_data='Учебная активность')
    builder.button(text='Научная активность', callback_data='Научная активность')
    builder.button(text='Социальная активность', callback_data='Социальная активность')
    builder.button(text='Культурно досуговая активность', callback_data='Культурно досуговая активность')
    builder.button(text='Готово', callback_data='done')
    builder.adjust(2)

    await message.answer('Выберите вид своего достижения (можно несколько если не уверены)',
                         reply_markup=ReplyKeyboardRemove())

    await message.answer(
        'Текущий список: пусто',
        reply_markup=builder.as_markup(resize_keyboard=True)
    )

@add_achievement.callback_query(item_selection.choosing, F.data.in_(['Учебная активность', 'Научная активность',
                                                                     'Социальная активность', 'Культурно досуговая активность']))
async def add_item(callback: CallbackQuery, state: FSMContext ):
    data = await state.get_data()
    items = data.get('items', [])

    if callback.data in items:
        text = f'Вы уже выбрали {html.bold(callback.data)}\n'\
               f'Пожалуйста, выберите другой вид или нажмите "Готово"'

    else:
        items.append(callback.data)
        await state.update_data(items=items)


        current_list = ', '.join(items) if items else 'пусто'
        text = f'Текущий список: {current_list}'

    builder = InlineKeyboardBuilder()
    builder.button(text='Учебная активность', callback_data='Учебная активность')
    builder.button(text='Научная активность', callback_data='Научная активность')
    builder.button(text='Социальная активность', callback_data='Социальная активность')
    builder.button(text='Культурно досуговая активность', callback_data='Культурно досуговая активность')
    builder.button(text='Готово', callback_data='done')
    builder.adjust(2)

    await callback.message.edit_text(text, reply_markup=builder.as_markup(resize_keyboard=True))
    await callback.answer()

@add_achievement.callback_query(item_selection.choosing, F.data == 'done')
async def done_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    items = data.get('items', [])

    if not items:
        await callback.answer(text='Вы ничего не выбрали', show_alert=True)
        return

    await state.set_state(item_selection.waiting_for_file)
    text = ', '.join(items)
    await callback.message.edit_text(text=f'Вы выбрали: {html.bold(text)}\n\n'
                                          f'Теперь отправьте файл или фотографию, подтверждающую ваше достижение')
    await callback.answer()

@add_achievement.message(item_selection.waiting_for_file, F.photo | F.document)
async def file_handler(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    items = data.get('items', [])

    tg_list = is_user_register(message.from_user.username)
    tg_id_from_db = tg_list[0]

    if message.photo:
        file_id = message.photo[-1].file_id
        file_type = 'photo'
    else:
        file_id = message.document.file_id
        file_type = 'document'

    file_path = await save_file_to_disk(bot, file_id)
    await state.update_data(file_id = file_id, file_type = file_type)

    user_name = message.from_user.username
    status = 'viewing'
    print(tg_id_from_db)
    await add_bd_achievement(AchievementAddSchema(
        user_tg_id=tg_id_from_db,
        status=status,
        categories=', '.join(items),
        file_path=file_path,
        file_type=file_type
    ))
    await message.answer('Достижение отправлено на проверку')
    await state.clear()


@add_achievement.message(item_selection.waiting_for_file)
async def invalid_file_handler(message: Message):
    await message.answer('Пожалуйста отправьте фото или файл')

async def main():
    #Настройка прокси сервера для корректной работы с телеграммом
    proxy_url = 'http://127.0.0.1:10801'
    session = AiohttpSession(proxy=proxy_url)

    bot = Bot(token=token, session=session, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp = Dispatcher()
    dp.include_router(menu)
    dp.include_router(add_achievement)
    dp.include_router(admin_router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())