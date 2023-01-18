from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from tgbot.misc.throttling_function import rate_limit


@rate_limit(5)
async def bot_echo_message(message: types.Message, state: FSMContext):
    await message.answer("😔 Команда не распознана. Если что-то пошло не так - нажмите <b>/restart</b>.")


@rate_limit(5)
async def bot_echo_callback(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("😔 Что-то пошло не так. Нажмите <b>/restart</b>.")


def register_echo(dp: Dispatcher):
    dp.register_message_handler(bot_echo_message, state="*", content_types=types.ContentTypes.ANY)
    dp.register_callback_query_handler(bot_echo_callback, state="*")
