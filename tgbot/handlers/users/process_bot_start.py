from aiogram import types, Dispatcher

from tgbot.keyboards.default.base_keyboards import main_menu_kb
from tgbot.misc.throttling_function import rate_limit
from tgbot.services.database import db_commands


@rate_limit(5)
async def bot_start(message: types.Message):
    await message.answer("Привет! Это тестовый бот для создания опросов и вывода статистики по их окончании.",
                         reply_markup=main_menu_kb)
    await db_commands.add_user(id=message.from_user.id, name=message.from_user.full_name)


def register_process_bot_start(dp: Dispatcher):
    dp.register_message_handler(bot_start, commands=["start"], state="*")
