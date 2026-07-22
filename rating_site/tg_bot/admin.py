import json

from aiogram import html, F, Router
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile

import os

from rating_site.env_loader import admin_id

from rating_site.tg_bot.sql_get_func import (
    get_viewing_requests_count,
    get_all_viewing_requests,
)

from rating_site.tg_bot.sql_post_func import (
    update_request,
    ban_user_by_tg_user_name
)

from rating_site.tg_bot.keyboards import admin_keyboard, request_keyboard

from rating_site.backend.db_get_requests import get_category_data

admin_r = Router()

admin_id = int(admin_id)


class AdminStates(StatesGroup):
    reviewing = State()
    choosing = State()
    rate = State()

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

    categories = json.loads(categories)

    category_data_map = await get_category_data()
    category_list = []

    for category, category_data in category_data_map.items():
        if category_data['id'] in categories:
            category_list.append(category)

    category_str = ', '.join(category_list)

    if description:
        caption = (f'Достижение от: @{html.bold(user_name)}\n\n'
                   f'{html.bold(category_str)}\n\n'
                   f'{html.bold('Описание:')}\n'
                   f'{description}')
    else:
        caption = (f'Достижение от: @{html.bold(user_name)}\n\n'
                   f'{html.bold(category_str)}')

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

    await state.update_data(temp_request_id=request_id)
    await state.set_state(AdminStates.choosing)
    await type_keyboard_show(callback, state)

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
    await update_request(request_id, 'deny')
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

    await update_request(request_id, status='approve', category=request_type, grade=grade)
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

