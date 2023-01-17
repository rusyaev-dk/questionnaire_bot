from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from tgbot.misc.throttling_function import rate_limit


@rate_limit(5)
async def bot_echo(message: types.Message):
    await message.answer("😔 Команда не распознана. Попробуйте <b>/restart</b>.")


@rate_limit(5)
async def bot_echo_all(message: types.Message, state: FSMContext):
    await message.answer("😔 Команда не распознана. Попробуйте <b>/restart</b>.")


def register_echo(dp: Dispatcher):
    dp.register_message_handler(bot_echo)
    dp.register_message_handler(bot_echo_all, state="*", content_types=types.ContentTypes.ANY)
