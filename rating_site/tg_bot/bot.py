from aiogram import Dispatcher, Bot, html, F, Router
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

import uuid

import asyncio

from rating_site.backend.db_post_requests import add_bd_achievement
from rating_site.backend.schems import (
    AchievementAddSchema,
    AchievementFileSchema,
)
from rating_site.backend.db_get_requests import get_category_data

from rating_site.tg_bot.admin import admin_r as admin_router

from rating_site.env_loader import (
    token,
    proxy_url
)

from rating_site.tg_bot.sql_get_func import (
    is_user_register,
    is_valid_login,
    linked_telegrams,
)
from rating_site.tg_bot.sql_post_func import (
    add_tg_user_name_in_db,
)

from pathlib import Path

##########Добавить очистку из telegram_data по user_id = login

menu = Router()
add_achievement = Router()

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)

async def save_file_to_disk(bot, file_id):
    file = await bot.get_file(file_id)
    ext = file.file_path.split('.')[-1] if '.' in file.file_path else 'bin'
    filename = f'{uuid.uuid4()}.{ext}'

    absolute_file_path = DATA_DIR / filename
    relative_file_path = Path("data") / filename

    await bot.download_file(file.file_path, destination=absolute_file_path)

    return relative_file_path

class item_selection(StatesGroup):
    enter_login = State()
    confirm_linking = State()
    choosing = State()
    waiting_for_file = State()
    waiting_for_description = State()

@menu.message(Command('start', 'register'))
async def command_start_handler(message: Message, state: FSMContext):
    user_name = message.from_user.username
    tg_list = is_user_register(user_name)

    if tg_list:
        is_banned = tg_list[1]
        if is_banned:
            await message.answer('Вы были заблокированы администратором')
            return
        await show_main_menu(message)
    else:
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
    tg_username = message.from_user.username

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

    await finish_linking(message, tg_username, user_id, real_name, state)

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
        await show_main_menu(source)

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
async def add_item(callback: CallbackQuery, state: FSMContext):
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
async def request_commit(message: Message, state: FSMContext):
    if message.photo:
        file_id = message.photo[-1].file_id
        file_type = 'photo'
    else:
        file_id = message.document.file_id
        file_type = 'document'

    await state.update_data(file_id=file_id, file_type=file_type)

    builder = InlineKeyboardBuilder()
    builder.button(text='Отправить', callback_data='send')
    builder.button(text='Добавить описание', callback_data='add_description')
    builder.adjust(1)

    await message.answer('Проверьте, что все введено правильно\n'
                         'Что то не так? Начните заново с /start',
                         reply_markup=builder.as_markup(resize_keyboard=True))


@add_achievement.callback_query(item_selection.waiting_for_file, F.data == 'send')
async def file_handler(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    items = data.get('items', [])

    file_id = data.get('file_id')
    file_type = data.get('file_type')
    description = data.get('description', None)

    tg_list = is_user_register(callback.from_user.username)
    tg_id_from_db = tg_list[0]

    file_path = await save_file_to_disk(bot, file_id)

    category_data_map = await get_category_data()
    category_ids = []

    status = 'viewing'
    for category in items:
        category_id = (category_data_map.get(category))['id']
        category_ids.append(category_id)

    await add_bd_achievement(AchievementAddSchema(
        user_tg_id=tg_id_from_db,
        status=status,
        category_id=category_ids,
        grade = 0.0,
        description=description,
        file_info=AchievementFileSchema(
            file_type=file_type,
            file_path=file_path.as_posix(),
        )
    ))
    await callback.message.answer('Достижение отправлено на проверку')
    await state.clear()
    await callback.answer()

@add_achievement.callback_query(item_selection.waiting_for_file, F.data == 'add_description')
async def send_add_description_message(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text='Введите описание к заявке:')

    await state.set_state(item_selection.waiting_for_description)
    await callback.message.edit_text('Введите описание к заявке (до 500 символов)')
    await callback.answer()

@add_achievement.message(item_selection.waiting_for_description, F.text)
async def save_description(message: Message, state: FSMContext):
    description = message.text.strip()

    if len(description) > 500:
        await message.answer('Описание слищеом длинное. Попробуйте снова')
        return

    await state.update_data(description=description)
    await state.set_state(item_selection.waiting_for_file)

    builder = InlineKeyboardBuilder()
    builder.button(text='Отправить', callback_data='send')
    builder.button(text='Изменить описание', callback_data='add_description')
    builder.adjust(1)

    await message.answer('Описание сохранено\n'
                         'Теперь вы можете отправить заявку',
                         reply_markup=builder.as_markup(resize_keyboard=True))


@add_achievement.message(item_selection.waiting_for_file)
async def invalid_file_handler(message: Message):
    await message.answer('Пожалуйста отправьте фото или файл')

async def main():
    #Настройка прокси сервера для корректной работы с телеграммом
    session = (AiohttpSession(proxy=proxy_url) if proxy_url else AiohttpSession())

    bot = Bot(token=token, session=session, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp = Dispatcher()
    dp.include_router(menu)
    dp.include_router(add_achievement)
    dp.include_router(admin_router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())