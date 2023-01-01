import re
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import ReplyKeyboardRemove

from tgbot.keyboards.default.base_keyboards import main_menu_kb
from tgbot.misc.states import FillQe
from tgbot.misc.throttling_function import rate_limit
from tgbot.services.database import db_commands
from tgbot.services.database.db_commands import increase_started_by


@rate_limit(3)
async def bot_start(message: types.Message):
    await message.answer("Привет! Это <b>тестовый</b> бот для создания опросов и прохождения их другими людьми. "
                         "Пока что бот находится на ранней стадии своего развития, так что могут возникать ошибки!",
                         reply_markup=main_menu_kb)
    await db_commands.add_user(id=message.from_user.id, name=message.from_user.full_name)


@rate_limit(3)
async def deep_link_start(message: types.Message, state: FSMContext):
    args = message.get_args()
    await db_commands.add_user(id=message.from_user.id, name=message.from_user.full_name)
    if len(args) == 10:
        qe_text_answers = await db_commands.select_qe_text_answers(quest_id=args, respondent_id=message.from_user.id)
        if qe_text_answers:
            await message.answer(f"Опрос <b>{qe_text_answers.title}</b> уже пройден Вами!", reply_markup=main_menu_kb)
        else:
            questionnaire = await db_commands.select_questionnaire(quest_id=args)
            if questionnaire:
                if questionnaire.is_active == "true":

                    await increase_started_by(quest_id=questionnaire.quest_id)
                    await message.answer(f"Вы начали прохождение опроса: "
                                         f"{questionnaire.title}\n"
                                         f"Вопрос 1: {questionnaire.questions[0]}",
                                         reply_markup=ReplyKeyboardRemove())
                    await state.update_data(quest_id=questionnaire.quest_id, counter=1,
                                            answers_quantity=questionnaire.questions_quantity)
                    await db_commands.create_qe_text_answers(quest_id=questionnaire.quest_id,
                                                             respondent_id=message.from_user.id,
                                                             answers_quantity=questionnaire.questions_quantity,
                                                             title=questionnaire.title)
                    await FillQe.A1.set()
                else:
                    await message.answer("⛔️ Данный опрос был остановлен автором.", reply_markup=main_menu_kb)
            else:
                await message.answer("🚫 Опрос не найден.", reply_markup=main_menu_kb)
    else:
        await message.answer("❗️ Ссылка, по которой Вы перешли, недействительна.", reply_markup=main_menu_kb)


def register_process_bot_start(dp: Dispatcher):
    dp.register_message_handler(deep_link_start, CommandStart(deep_link=re.compile(r"^[a-zA-Z0-9]{1,10}$")), state="*")
    dp.register_message_handler(bot_start, CommandStart(), state="*")
