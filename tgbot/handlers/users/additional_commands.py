from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from tgbot.keyboards.qe_reply_kbs import main_menu_kb
from tgbot.misc.throttling_function import rate_limit

from tgbot.services.database import db_commands
from tgbot.misc.dependences import ADMIN_USERNAME


@rate_limit(2)
async def get_main_menu(message: types.Message, state: FSMContext):
    await db_commands.add_user(id=message.from_user.id, name=message.from_user.full_name)
    state_name = await state.get_state()
    if state_name:
        if "CreateQe" in state_name:
            await message.answer("❌ Создание опроса отменено. Главное меню:", reply_markup=main_menu_kb)
        elif "PassQe" in state_name:
            await message.answer("❌ Прохождение опроса отменено. Главное меню:", reply_markup=main_menu_kb)
        else:
            await message.answer("Главное меню:", reply_markup=main_menu_kb)
    else:
        await message.answer("Главное меню:", reply_markup=main_menu_kb)

    await state.reset_data()
    await state.finish()


@rate_limit(2)
async def cancel_action(message: types.Message, state: FSMContext):
    state_name = await state.get_state()
    if state_name:
        if "CreateQe" in state_name:
            await message.answer("❌ Создание опроса отменено. Главное меню:", reply_markup=main_menu_kb)
        elif "PassQe" in state_name:
            await message.answer("❌ Прохождение опроса отменено. Главное меню:", reply_markup=main_menu_kb)
        else:
            await message.answer("↩️ Текущее действие отменено. Главное меню:", reply_markup=main_menu_kb)
    else:
        await message.answer("↩️ Текущее действие отменено. Главное меню:", reply_markup=main_menu_kb)

    await state.reset_data()
    await state.finish()


@rate_limit(2)
async def get_help(message: types.Message):
    await message.answer("🛠 Если что-то пошло не так, нажмите <b>/restart</b>, чтобы перезапустить бота. "
                         f"Пожалуйста, сообщите об ошибке разработчику: <b>{ADMIN_USERNAME}</b>")


@rate_limit(3)
async def get_bot_statistics(message: types.Message):
    total_users = await db_commands.count_users()
    total_qes = await db_commands.count_qes()
    await message.answer("📊 Статистика бота:\n"
                         f"• Зарегистрировано пользователей: <b>{total_users}</b> чел.\n"
                         f"• Создано опросов: <b>{total_qes}</b>\n")


def register_additional_commands(dp: Dispatcher):
    dp.register_message_handler(get_main_menu, commands=["menu"], state="*")
    dp.register_message_handler(cancel_action, commands=["cancel"], state="*")
    dp.register_message_handler(get_help, commands=["help"], state="*")

    dp.register_message_handler(get_bot_statistics, commands=["statistics"], is_admin=True, state="*")
