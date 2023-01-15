from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from tgbot.keyboards.default.qe_text_keyboards import main_menu_kb
from tgbot.misc.throttling_function import rate_limit

from tgbot.services.database import db_commands
from tgbot.misc.dependences import ADMIN_USERNAME


@rate_limit(5)
async def get_main_menu(message: types.Message, state: FSMContext):
    await message.answer("Главное меню:", reply_markup=main_menu_kb)
    await state.finish()


@rate_limit(5)
async def restart_bot(message: types.Message, state: FSMContext):
    await message.answer("♻️ Бот перезапущен. Главное меню:", reply_markup=main_menu_kb)
    await state.finish()


@rate_limit(5)
async def get_help(message: types.Message):
    await message.answer("🛠 Если что-то пошло не так, нажмите на команду <b>/restart</b>, чтобы перезапустить бота. "
                         f"Пожалуйста, сообщите об ошибке разработчику: <b>{ADMIN_USERNAME}</b>")


@rate_limit(5)
async def get_bot_statistics(message: types.Message):
    total_users = await db_commands.count_users()
    total_qes = await db_commands.count_qes()
    await message.answer("📊 Статистика бота:\n"
                         f"• Зарегистрировано пользователей: <b>{total_users}</b> чел.\n"
                         f"• Создано опросов: <b>{total_qes}</b>\n")


def register_service_commands(dp: Dispatcher):
    dp.register_message_handler(get_main_menu, commands=["main_menu"], state="*")
    dp.register_message_handler(restart_bot, commands=["restart"], state="*")
    dp.register_message_handler(get_help, commands=["help"], state="*")

    dp.register_message_handler(get_bot_statistics, commands=["statistics"], is_admin=True, state="*")
