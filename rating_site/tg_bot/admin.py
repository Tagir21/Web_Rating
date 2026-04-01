from aiogram import Dispatcher, Bot, html, F, Router
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardMarkup, InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from dotenv import dotenv_values
import asyncio

admin_id = int(dotenv_values('.env')['ADMIN_ID'])

admin_r = Router()

def admin_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text='Просмотреть заявки', callback_data='look')

    return builder

@admin_r.message(Command('admin'))
async def admin_panel(message: Message):
    print(f'{admin_id}'
          f'\n{message.from_user.id}')
    if message.from_user.id != admin_id:
        await message.answer('У вас нет доступа к этой команду (фу уйди)')
        return
    await message.answer('Добро пожаловать', reply_markup=admin_keyboard().as_markup())