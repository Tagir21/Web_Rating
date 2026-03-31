from aiogram import Dispatcher, Bot, html, F, Router
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardMarkup, InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from dotenv import dotenv_values
import asyncio

# Получение токена бота из переменной окружения .env
token = dotenv_values('.env')['BOT_TOKEN']

menu = Router()
add_achievement = Router()

class item_selection(StatesGroup):
    choosing = State()

@menu.message(Command('start', 'register'))
async def command_start_handler(message: Message):
    builder = ReplyKeyboardBuilder()
    builder.button(text='Добавить достижение')
    builder.button(text='Помощь')
    builder.button(text='Другое')
    builder.adjust(2)
    await message.answer(f'Здравствуйте, {html.bold(message.from_user.full_name)}!\n'
                         f'Добро пожаловать в 317kaf бот\n'
                         f'Выберите желаемое действие',
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

    await message.answer(
        'Выберите вид своего достижения (можно несколько, если не уверены)\n'
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
        text = 'Выберите вид своего достижения (можно несколько, если не уверены)\n'\
               f'Текущий список: {current_list}'

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

    await callback.message.edit_text(text='Ура')
    await callback.answer()

    await state.clear()

async def main():
    #Настройка прокси сервера для корректной работы с телеграммом
    proxy_url = 'http://127.0.0.1:10801'
    session = AiohttpSession(proxy=proxy_url)

    bot = Bot(token=token, session=session, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp = Dispatcher()
    dp.include_router(menu)
    dp.include_router(add_achievement)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())