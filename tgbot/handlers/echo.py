from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from tgbot.misc.throttling_function import rate_limit


@rate_limit(2)
async def bot_echo_message(message: types.Message, state: FSMContext):
    state = await state.get_state()
    if state == "CreateQe:QuestionType":
        await message.answer("⬆️ Пожалуйста, укажите <b>тип</b> вопроса, выбрав соответствующий пункт выше.\n"
                             "❌ Чтобы прекратить создание опроса - нажмите <b>/cancel</b>")
    elif state == "PassQe:ClosedAnswer":
        await message.answer("⬆️ Пожалуйста, укажите <b>вариант</b> ответа, выбрав соответствующий пункт выше.\n"
                             "❌ Чтобы прекратить прохождение опроса - нажмите <b>/cancel</b>")
    else:
        await message.answer("😔 Команда не распознана. Если что-то пошло не так - нажмите <b>/restart</b>")


@rate_limit(2)
async def bot_echo_callback(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("😔 Что-то пошло не так. Пожалуйста, нажмите <b>/restart</b>")


def register_echo(dp: Dispatcher):
    dp.register_message_handler(bot_echo_message, content_types=types.ContentTypes.ANY, state="*")
    dp.register_callback_query_handler(bot_echo_callback, state="*")
