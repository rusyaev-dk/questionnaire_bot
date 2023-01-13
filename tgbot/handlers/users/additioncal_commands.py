from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from tgbot.keyboards.default.qe_text_keyboards import main_menu_kb
from tgbot.services.dependences import ADMIN_USERNAME


async def get_main_menu(message: types.Message, state: FSMContext):
    await message.answer("Главное меню:", reply_markup=main_menu_kb)
    await state.finish()


async def restart_bot(message: types.Message, state: FSMContext):
    await message.answer("♻️ Бот перезапущен. Главное меню:", reply_markup=main_menu_kb)
    await state.finish()


async def get_help(message: types.Message):
    await message.answer("🛠 Если что-то пошло не так, нажмите на команду <b>/restart</b>, чтобы перезапустить бота. "
                         f"Пожалуйста, сообщите об ошибке разработчику: <b>{ADMIN_USERNAME}</b>")


def register_service_commands(dp: Dispatcher):
    dp.register_message_handler(get_main_menu, commands=["main_menu"], state="*")
    dp.register_message_handler(restart_bot, commands=["restart"], state="*")
    dp.register_message_handler(get_help, commands=["help"], state="*")
