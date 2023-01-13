from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove

from tgbot.keyboards.default.qe_text_keyboards import main_menu_kb
from tgbot.keyboards.inline.additional_inline_keyboards import notify_users_approve_callback, notify_users_approves, \
    notify_users_approve_kb
from tgbot.misc.states import NotifyUsers
from tgbot.services.database import db_commands
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


async def get_bot_statistics(message: types.Message):
    total_users = await db_commands.count_users()
    total_qes = await db_commands.count_qes()
    await message.answer("📊 Статистика бота:\n"
                         f"• Пользователей: <b>{total_users}</b> чел.\n"
                         f"• Опросов: <b>{total_qes}</b> шт.\n")


async def notify_users(message: types.Message):
    await message.answer("Отправьте текст/медиа для отправки пользователям:", reply_markup=ReplyKeyboardRemove())
    await NotifyUsers.NotifyMedia.set()


async def get_notify_media(message: types.Message, state: FSMContext):
    if message.document:
        await message.answer("Вы хотите отправить документ")
    elif message.photo:
        await message.answer("Вы хотите отправить ФОТО")
    else:
        await message.answer("Вы хотите отправить ТЕКСТ")
    await message.answer("Подтвердите отправку:", reply_markup=notify_users_approve_kb)
    await NotifyUsers.NotifyApprove.set()


async def notify_approve(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    approve = callback_data.get("approve")
    if approve == "send":
        users = await db_commands.select_all_users()
        # for user in users:
        #     await call.bot.send
    else:
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text="❌ Отправка отменена")
        await call.message.answer("Главное меню:", reply_markup=main_menu_kb)
    await state.finish()


def register_service_commands(dp: Dispatcher):
    dp.register_message_handler(get_main_menu, commands=["main_menu"], state="*")
    dp.register_message_handler(restart_bot, commands=["restart"], state="*")
    dp.register_message_handler(get_help, commands=["help"], state="*")

    dp.register_message_handler(get_bot_statistics, commands=["statistics"], is_admin=True, state="*")
    dp.register_message_handler(notify_users, commands=["notify_users"], is_admin=True, state="*")

    notify_content = [types.ContentType.TEXT, types.ContentType.PHOTO, types.ContentType.DOCUMENT,
                      types.ContentType.DICE]

    dp.register_message_handler(get_notify_media, content_types=notify_content, is_admin=True,
                                state=NotifyUsers.NotifyMedia)
    dp.register_callback_query_handler(notify_approve,
                                       notify_users_approve_callback.filter(approves=notify_users_approves),
                                       is_admin=True, state=NotifyUsers.NotifyApprove)
