import re
import time

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart

from tgbot.keyboards.default.qe_text_keyboards import main_menu_kb
from tgbot.keyboards.inline.qe_inline_keyboards import replay_qe_approve_kb, replay_qe_approve_callback, \
    replay_approves, generate_answer_options
from tgbot.misc.states import PassQe
from tgbot.misc.throttling_function import rate_limit
from tgbot.services.database import db_commands
from tgbot.services.database.db_commands import increase_qe_started_by
from tgbot.services.service_functions import parse_answer_options


@rate_limit(3)
async def bot_start(message: types.Message):
    await message.answer("🤖 Привет! Это <b>тестовый</b> бот для создания опросов и прохождения их другими людьми. "
                         "Пока что он находится на ранней стадии своего развития, так что могут возникать ошибки!",
                         reply_markup=main_menu_kb)
    await db_commands.add_user(id=message.from_user.id, name=message.from_user.full_name)


@rate_limit(3)
async def deeplink_bot_start(message: types.Message, state: FSMContext):
    qe_id = message.get_args()
    await db_commands.add_user(id=message.from_user.id, name=message.from_user.full_name)
    if len(qe_id) == 10:
        questionnaire = await db_commands.select_questionnaire(qe_id=qe_id)
        if questionnaire:
            passed = await db_commands.is_passed(respondent_id=message.from_user.id, qe_id=qe_id)
            if passed:
                await message.answer(f"❗️ Вы уже прошли опрос <b>{questionnaire.title}</b>. Хотите пройти его "
                                     "заново? В этом случае Ваши предыдущие ответы будут удалены.",
                                     reply_markup=replay_qe_approve_kb)
                await state.set_state("replay_qe_approve")
                await state.update_data(qe_id=qe_id)
            else:
                if questionnaire.is_active == "true":
                    await increase_qe_started_by(qe_id=questionnaire.qe_id)
                    questions = await db_commands.select_questions(qe_id=qe_id)
                    question = questions[0]

                    if question.question_type == "open":
                        await message.answer(f"🔍 Вы начали прохождение опроса: {questionnaire.title}\n"
                                             f"❓ 1-й вопрос: {question.question_text}")
                        await PassQe.OpenAnswer.set()
                    else:
                        answer_options = await db_commands.select_answer_options(question_id=question.question_id)
                        text = await parse_answer_options(answer_options=answer_options)
                        await message.answer(f"🔍 Вы начали прохождение опроса: {questionnaire.title}\n"
                                             f"❓ 1-й вопрос: {question.question_text}\n\n{text}",
                                             reply_markup=generate_answer_options(options_quantity=len(answer_options)))
                        await PassQe.ClosedAnswer.set()
                    start_time = time.time()
                    await state.update_data(qe_id=questionnaire.qe_id, counter=0, start_time=start_time,
                                            answers_quantity=questionnaire.questions_quantity)
                else:
                    await message.answer("⛔️ Данный опрос был остановлен автором. Пожалуйста, попробуйте позже.",
                                         reply_markup=main_menu_kb)
        else:
            await message.answer("🚫 Опрос не найден.", reply_markup=main_menu_kb)
    else:
        await message.answer("❗️ Ссылка, по которой Вы перешли, недействительна.", reply_markup=main_menu_kb)


async def replay_qe_approve(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    approve = callback_data.get("approve")
    if approve == "cancel":
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text="❌ Прохождение опроса отменено")
        await call.message.answer("Главное меню:", reply_markup=main_menu_kb)
        await state.finish()
    else:
        data = await state.get_data()
        qe_id = data.get("qe_id")
        questionnaire = await db_commands.select_questionnaire(qe_id=qe_id)
        if questionnaire:
            if questionnaire.is_active == "true":
                await db_commands.delete_user_answers(respondent_id=call.from_user.id, qe_id=qe_id)  # !!!
                await db_commands.delete_user_passed_qe(respondent_id=call.from_user.id, qe_id=qe_id)
                await db_commands.decrease_passed_by(qe_id=qe_id)

                # await increase_qe_started_by(qe_id=questionnaire.qe_id)
                questions = await db_commands.select_questions(qe_id=qe_id)
                question = questions[0]

                if question.question_type == "open":
                    await call.message.answer(f"🔍 Вы начали прохождение опроса: {questionnaire.title}\n"
                                              f"❓ 1-й вопрос: {question.question_text}")
                    await PassQe.OpenAnswer.set()
                else:
                    answer_options = await db_commands.select_answer_options(question_id=question.question_id)
                    text = await parse_answer_options(answer_options=answer_options)
                    await call.message.answer(f"🔍 Вы начали прохождение опроса: {questionnaire.title}\n"
                                              f"❓ 1-й вопрос: {question.question_text}\n\n{text}",
                                              reply_markup=generate_answer_options(options_quantity=len(answer_options)))
                    await PassQe.ClosedAnswer.set()

                start_time = time.time()
                await state.update_data(qe_id=questionnaire.qe_id, counter=0, start_time=start_time,
                                        answers_quantity=questionnaire.questions_quantity)
            else:
                await call.message.answer("⛔️ Данный опрос был остановлен автором. Пожалуйста, попробуйте позже.",
                                          reply_markup=main_menu_kb)
        else:
            await call.message.answer("🚫 Опрос не найден.", reply_markup=main_menu_kb)


def register_bot_start(dp: Dispatcher):
    dp.register_message_handler(deeplink_bot_start, CommandStart(deep_link=re.compile(r"^[a-zA-Z0-9]{1,10}$")),
                                state="*")
    dp.register_callback_query_handler(replay_qe_approve, replay_qe_approve_callback.filter(approve=replay_approves),
                                       state="replay_qe_approve")
    dp.register_message_handler(bot_start, CommandStart(), state="*")
