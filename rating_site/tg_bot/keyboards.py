from aiogram.utils.keyboard import InlineKeyboardBuilder

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