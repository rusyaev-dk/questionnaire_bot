import re
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart

from tgbot.keyboards.default.base_keyboards import main_menu_kb
from tgbot.misc.states import FillQE
from tgbot.misc.throttling_function import rate_limit
from tgbot.services.database import db_commands


@rate_limit(8)
async def bot_start(message: types.Message):
    await message.answer("Привет! Это тестовый бот для создания опросов и вывода статистики по их окончании.",
                         reply_markup=main_menu_kb)
    await db_commands.add_user(id=message.from_user.id, name=message.from_user.full_name)


async def deep_link_start(message: types.Message, state: FSMContext):
    args = message.get_args()
    if len(args) == 10:
        questionnaire = await db_commands.select_questionnaire(quest_id=args)
        if questionnaire:
            await message.answer(f"Вы начали прохождение опроса: "
                                 f"{questionnaire.title}\n"
                                 f"Вопрос 1: {questionnaire.questions[0]}")
            await state.update_data(quest_id=questionnaire.quest_id)
            await FillQE.A1.set()
        else:
            await message.answer("Опрос не найден...",
                                 reply_markup=main_menu_kb)
    else:
        await message.answer("Ссылка, по которой Вы перешли, недействительна...",
                             reply_markup=main_menu_kb)


def register_process_bot_start(dp: Dispatcher):
    dp.register_message_handler(deep_link_start, CommandStart(deep_link=re.compile(r"^[a-zA-Z0-9]{1,10}$")), state="*")
    dp.register_message_handler(bot_start, CommandStart(), state="*")
