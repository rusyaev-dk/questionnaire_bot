import asyncio
import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove

from tgbot.keyboards.qe_reply_kbs import main_menu_kb
from tgbot.keyboards.additional_inline_kbs import notify_users_approve_callback, notify_users_approves, \
    notify_users_approve_kb
from tgbot.misc.states import NotifyUsers
from tgbot.misc.throttling_function import rate_limit
from tgbot.services.broadcast_functions import send_text, send_photo, send_document
from tgbot.services.database import db_commands


@rate_limit(5)
async def notify_users(message: types.Message):
    await message.answer("📦 Отправьте текст/фото/файл для оповещения пользователей:", reply_markup=ReplyKeyboardRemove())
    await NotifyUsers.NotifyMedia.set()


async def get_notify_media(message: types.Message, state: FSMContext):
    await message.answer("📬 Пользователям придёт следующее уведомление:")

    if message.text:
        await message.answer(message.text)
        await state.update_data(msg_type="text", text=message.text)

    elif message.photo:
        await message.answer_photo(photo=message.photo[-1].file_id, caption=message.caption)
        await state.update_data(msg_type="photo", photo_id=message.photo[-1].file_id, caption=message.caption)

    elif message.document:
        await message.answer_document(document=message.document.file_id, caption=message.caption)
        await state.update_data(msg_type="document", document_id=message.document.file_id, caption=message.caption)

    await message.answer("Подтвердите отправку:", reply_markup=notify_users_approve_kb)
    await NotifyUsers.NotifyApprove.set()


async def notify_approve(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    approve = callback_data.get("approve")

    if approve == "send":
        data = await state.get_data()
        users = await db_commands.select_all_users()
        msg_type = data.get("msg_type")

        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text="✅ Бот начал рассылку.")
        await call.message.answer("Главное меню:", reply_markup=main_menu_kb)
        counter = 0

        if msg_type == "text":
            text = data.get("text")
            try:
                for user in users:
                    if await send_text(bot=call.bot, user_id=user.id, text=text, disable_notification=True):
                        counter += 1
                    await asyncio.sleep(0.1)
            finally:
                await call.message.answer(f"📬 Успешно отправлено сообщений: {counter}")
                logging.info(f"Successfully sent messages: {counter}")

        elif msg_type == "photo":
            photo_id = data.get("photo_id")
            caption = data.get("caption")
            try:
                for user in users:
                    if await send_photo(bot=call.bot, user_id=user.id, photo_id=photo_id, caption=caption,
                                        disable_notification=True):
                        counter += 1
                    await asyncio.sleep(0.1)
            finally:
                await call.message.answer(f"📬 Успешно отправлено сообщений: {counter}")
                logging.info(f"Successfully sent messages: {counter}")

        elif msg_type == "document":
            document_id = data.get("document_id")
            caption = data.get("caption")
            try:
                for user in users:
                    if await send_document(bot=call.bot, user_id=user.id, document_id=document_id, caption=caption,
                                           disable_notification=True):
                        counter += 1
                    await asyncio.sleep(0.1)
            finally:
                await call.message.answer(f"📬 Успешно отправлено сообщений: {counter}")
                logging.info(f"Successfully sent messages: {counter}")

    elif approve == "cancel":
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text="❌ Рассылка отменена.")
        await call.message.answer("Главное меню:", reply_markup=main_menu_kb)
    await state.reset_data()
    await state.finish()


def register_notify_users(dp: Dispatcher):
    notify_content = [types.ContentType.TEXT, types.ContentType.PHOTO, types.ContentType.DOCUMENT]
    dp.register_message_handler(notify_users, commands=["notify_users"], is_admin=True, state="*")
    dp.register_message_handler(get_notify_media, content_types=notify_content, is_admin=True,
                                state=NotifyUsers.NotifyMedia)
    dp.register_callback_query_handler(notify_approve,
                                       notify_users_approve_callback.filter(approve=notify_users_approves),
                                       is_admin=True, state=NotifyUsers.NotifyApprove)
