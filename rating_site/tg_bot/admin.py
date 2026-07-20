from aiogram import Dispatcher, Bot, html, F, Router
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardMarkup, InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, FSInputFile
from mysql.connector import connect

import os

from dotenv import dotenv_values
import asyncio

admin_id = int(dotenv_values('.env')['ADMIN_ID'])
db_hostname = dotenv_values('.env')['DB_HOSTNAME']
db_port = int(dotenv_values('.env')['DB_PORT'])
db_username = dotenv_values('.env')['DB_USERNAME']
db_password = dotenv_values('.env')['DB_PASSWORD']
db_name = dotenv_values('.env')['DB_NAME']

admin_r = Router()

class AdminStates(StatesGroup):
    reviewing = State()
    choosing = State()
    rate = State()

def admin_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text='Просмотреть', callback_data='look')

    return builder

def request_keyboard(request_id):
    builder = InlineKeyboardBuilder()
    builder.button(text='👍', callback_data=f'approve_{request_id}')
    builder.button(text='◀️', callback_data=f'back_{request_id}')
    builder.button(text='👎', callback_data=f'deny_{request_id}')
    builder.button(text='Заблокировать пользователя', callback_data=f'ban_{request_id}')
    builder.adjust(3)

    return builder

def bd_connect():
    conn = connect(host=db_hostname,
                   port=db_port,
                   username=db_username,
                   password=db_password,
                   database=db_name)
    cursor = conn.cursor()

    return conn, cursor

def get_viewing_requests_count():
    conn, cursor = bd_connect()
    cursor.execute(
        'SELECT COUNT(*) AS count FROM achievements WHERE status = "viewing"'
    )
    total_count = cursor.fetchone()[0]
    conn.close()

    return total_count

def get_all_viewing_requests():
    conn, cursor = bd_connect()
    cursor.execute('SELECT id, (SELECT tg_name FROM telegram_data WHERE telegram_data.id = user_tg_id),'
                   ' category, description, file_path, file_type'
                   ' FROM achievements WHERE status = "viewing"')
    all_viewing_requests = cursor.fetchall()
    conn.close()

    return all_viewing_requests

def update_request(request_id, status, category=None, grade=None):
    conn, cursor = bd_connect()
    if grade and category:
        cursor.execute('UPDATE achievements SET status = %s, category = %s, grade = %s WHERE id = %s',
                       (status, category, grade, request_id))
    else:
        cursor.execute('UPDATE achievements SET status = %s WHERE id = %s',
                       (status, request_id))
    conn.commit()
    conn.close()


def ban_user_by_tg_user_name(request_id):
    conn, cursor = bd_connect()
    cursor.execute('UPDATE telegram_data'
                   ' SET is_banned = 1'
                   ' WHERE id = (SELECT user_tg_id'
                   '             FROM achievements'
                   '             WHERE id = %s)', (request_id,))
    conn.commit()
    conn.close()

async def admin_panel(source):
    if isinstance(source, CallbackQuery):
        user_id = source.from_user.id
        reply_func = source.message.answer
        await source.answer()
    else:
        user_id = source.from_user.id
        reply_func = source.answer

    if user_id != admin_id:
        await reply_func('У вас нет доступа к этой команде (фу уйди)')
        return

    total_count = get_viewing_requests_count()
    await reply_func('Добро пожаловать\n'
                         f'Было создано {total_count} новых заявок',
                         reply_markup=admin_keyboard().as_markup())

@admin_r.message(Command('admin'))
async def admin(message: Message):
    await admin_panel(message)


@admin_r.callback_query(F.data == 'look')
async def show_requests(callback: CallbackQuery, state: FSMContext):
    requests = get_all_viewing_requests()

    if not requests:
        await callback.answer('Новых заявок нет')
        return

    await state.update_data(requests=requests, index=0)
    await state.set_state(AdminStates.reviewing)

    await send_request(callback, state)

async def send_request(source, state: FSMContext):
    if isinstance(source, CallbackQuery):
        reply_func = source.message
    else:
        reply_func = source

    data = await state.get_data()
    requests = data['requests']
    index = data['index']

    if index >= len(requests):
        await reply_func.answer('Все заявки обработаны')
        await state.clear()
        return

    request = requests[index]

    request_id = request[0]
    user_name = request[1]
    categories = request[2]
    description = request[3]
    file_path = request[4]
    file_type = request[5]

    if description:
        caption = (f'Достижение от: @{html.bold(user_name)}\n\n'
                   f'{html.bold(categories)}\n\n'
                   f'{html.bold('Описание:')}\n'
                   f'{description}')
    else:
        caption = (f'Достижение от: @{html.bold(user_name)}\n\n'
                   f'{html.bold(categories)}')

    await state.update_data(caption=caption)
    if os.path.exists(file_path):
        if file_type == 'photo':
            await reply_func.bot.send_photo(
                reply_func.chat.id,
                FSInputFile(file_path),
                caption=caption,
                reply_markup=request_keyboard(request_id).as_markup())
        else:
             await reply_func.bot.send_document(
                 reply_func.chat.id,
                 FSInputFile(file_path),
                 caption=caption,
                 reply_markup=request_keyboard(request_id).as_markup())
    else:
        await reply_func.answer(f'Файл не найден: {file_path}')
        await state.update_data(index=index+1)
        await send_request(reply_func, state)

@admin_r.callback_query(AdminStates.reviewing, F.data.startswith('approve'))
async def approve_request(callback: CallbackQuery, state: FSMContext):
    request_id = int(callback.data.split('_')[1])
    # update_request_status(request_id, 'approved')
    # await callback.answer('Заявка одобрена')

    await state.update_data(temp_request_id=request_id)
    await state.set_state(AdminStates.choosing)
    await type_keyboard_show(callback, state)
    print(request_id)

async def type_keyboard_show(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    request_id = data['temp_request_id']
    caption = data['caption']

    caption += '\n\n\nВыберите вид достижения:'

    builder = InlineKeyboardBuilder()
    builder.button(text='Учебная активность', callback_data='Учебная активность')
    builder.button(text='Научная активность', callback_data='Научная активность')
    builder.button(text='Социальная активность', callback_data='Социальная активность')
    builder.button(text='Культурно досуговая активность', callback_data='Культурно досуговая активность')
    builder.adjust(1)

    await callback.message.edit_caption(caption=caption, reply_markup=builder.as_markup(resize_keyboard=True))

@admin_r.callback_query(AdminStates.choosing, F.data.in_(['Учебная активность', 'Научная активность',
                                                          'Социальная активность', 'Культурно досуговая активность']))
async def type_choosing(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    caption = data['caption']
    caption += '\n\n\nВведите оценку за достижение (от 1 до 10):'

    request_type = callback.data
    await state.update_data(temp_request_type=request_type)
    await callback.message.edit_caption(caption=caption)
    await state.set_state(AdminStates.rate)
    await callback.answer()


@admin_r.callback_query(AdminStates.reviewing, F.data.startswith('deny'))
async def deny_request(callback: CallbackQuery, state: FSMContext):
    request_id = int(callback.data.split('_')[1])
    update_request(request_id, 'deny')
    await callback.answer('Заявка отклонена')

    data = await state.get_data()
    await state.update_data(index=data['index'] + 1)
    await send_request(callback, state)

@admin_r.message(AdminStates.rate, F.text)
async def rate_process(message: Message, state: FSMContext):
    try:
        grade = float(message.text.strip())
        if grade < 1 or grade > 10:
            raise ValueError
    except ValueError:
        await message.answer('Число неверно\nВведите число от 1 до 10')
        return

    data = await state.get_data()
    request_id = data['temp_request_id']
    request_type = data['temp_request_type']

    update_request(request_id, status='approve', category=request_type, grade=grade)
    await message.answer(f'Оценка {grade} выставлена. Заявка одобрена')

    await state.update_data(index=data['index'] + 1)
    await state.set_state(AdminStates.reviewing)
    await send_request(message, state)

@admin_r.callback_query(AdminStates.reviewing, F.data.startswith('ban'))
async def ban_user(callback: CallbackQuery, state: FSMContext):
    request_id = int(callback.data.split('_')[1])

    ban_user_by_tg_user_name(request_id)
    await callback.answer('Пользователь успешно заблокирован')

    data = await state.get_data()
    await state.update_data(index=data['index'] + 1)
    await send_request(callback, state)

@admin_r.callback_query(AdminStates.reviewing, F.data.startswith('back'))
async def back_user(callback: CallbackQuery, state: FSMContext):
    await admin_panel(callback)
    await state.clear()

