import re
import time
from math import fabs

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.markdown import quote_html

from tgbot.keyboards.qe_reply_kbs import main_menu_kb
from tgbot.keyboards.qe_inline_kbs import replay_qe_approve_kb, replay_qe_approve_callback, \
    replay_approves, parse_answer_options_kb, pass_qe_approve_kb, pass_qe_approve_callback, pass_qe_approves
from tgbot.misc.states import PassQe
from tgbot.misc.throttling_function import rate_limit
from tgbot.services.database import db_commands
from tgbot.services.database.db_commands import increase_qe_started_by
from tgbot.misc.dependences import WELCOME_MESSAGE
from tgbot.services.service_functions import parse_answer_options, get_average_completion_time


@rate_limit(2)
async def bot_start(message: types.Message):
    await message.answer(text=WELCOME_MESSAGE, reply_markup=main_menu_kb)
    await db_commands.add_user(id=message.from_user.id, name=message.from_user.full_name)


@rate_limit(2)
async def deeplink_bot_start(message: types.Message, state: FSMContext):
    qe_id = message.get_args()

    err_code = await db_commands.add_user(id=message.from_user.id, name=message.from_user.full_name)
    if err_code == 0:
        await message.answer(text=WELCOME_MESSAGE)

    if len(qe_id) == 10:
        questionnaire = await db_commands.select_questionnaire(qe_id=qe_id)
        if questionnaire:
            if questionnaire.is_active == "true":
                passed = await db_commands.is_passed(respondent_id=message.from_user.id, qe_id=qe_id)
                if passed:
                    await message.answer(f"❗️ Вы уже прошли опрос <b>{questionnaire.title}</b>."
                                         f" В случае повторного "
                                         f"прохождения предыдущие ответы будут <b>удалены</b>.",
                                         reply_markup=ReplyKeyboardRemove())
                    await message.answer("🔸 Пройти опрос заново?", reply_markup=replay_qe_approve_kb)
                    await state.update_data(qe_id=qe_id)
                    await PassQe.PassReplayApprove.set()
                else:
                    average_ct = await get_average_completion_time(qe_id=qe_id)
                    if fabs(average_ct[0]) < 10E-9:
                        text = "• Вы первый респондент этого опроса!"
                    else:
                        text = f"• Среднее время прохождения: <b>{average_ct[0]:.1f}</b> {average_ct[1]}"
                    await message.answer(f"• Опрос: <b>{questionnaire.title}</b>\n{text}",
                                         reply_markup=ReplyKeyboardRemove())
                    await message.answer(f"🔸 Начать прохождение опроса?", reply_markup=pass_qe_approve_kb)
                    await state.update_data(qe_id=qe_id)
                    await PassQe.PassBeginApprove.set()
            else:
                await message.answer("⛔️ Данный опрос был остановлен автором. Пожалуйста, попробуйте позже.",
                                     reply_markup=main_menu_kb)
        else:
            await message.answer("🚫 Опрос не найден.", reply_markup=main_menu_kb)
    else:
        await message.answer("❗️ Ссылка, по которой Вы перешли, недействительна.", reply_markup=main_menu_kb)


async def pass_qe_approve(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    approve = callback_data.get("approve")
    if approve == "pass":
        data = await state.get_data()
        qe_id = data.get("qe_id")

        questionnaire = await db_commands.select_questionnaire(qe_id=qe_id)
        await db_commands.increase_link_clicks(creator_id=questionnaire.creator_id)
        await increase_qe_started_by(qe_id=qe_id)
        questions = await db_commands.select_questions(qe_id=qe_id)
        question = questions[0]

        if question.question_type == "open":
            await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                             text=f"🔍 Вы начали прохождение опроса: {quote_html(questionnaire.title)}\n"
                                                  f"❓ 1-й вопрос: {quote_html(question.question_text)}")
            await PassQe.OpenAnswer.set()
        else:
            answer_options = await db_commands.select_answer_options(question_id=question.question_id)
            answer_options_text = await parse_answer_options(answer_options=answer_options)
            keyboard = parse_answer_options_kb(options_quantity=len(answer_options))
            await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                             text=f"🔍 Вы начали прохождение опроса: {questionnaire.title}\n"
                                                  f"❓ 1-й вопрос: {quote_html(question.question_text)}\n"
                                                  f"\n{quote_html(answer_options_text)}", reply_markup=keyboard)
            await state.update_data(question_id=question.question_id)
            await PassQe.ClosedAnswer.set()
        answer_start_time = time.time()
        await state.update_data(qe_id=questionnaire.qe_id, counter=0, answer_start_time=answer_start_time,
                                answers_quantity=questionnaire.questions_quantity, completion_time=0)
    elif approve == "cancel":
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text="❌ Прохождение опроса отменено.")
        await call.message.answer("Главное меню:", reply_markup=main_menu_kb)
        await state.reset_data()
        await state.finish()


async def replay_qe_approve(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    approve = callback_data.get("approve")
    if approve == "cancel":
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text="❌ Прохождение опроса отменено.")
        await call.message.answer("Главное меню:", reply_markup=main_menu_kb)
        await state.reset_data()
        await state.finish()
    else:
        data = await state.get_data()
        qe_id = data.get("qe_id")
        questionnaire = await db_commands.select_questionnaire(qe_id=qe_id)
        if questionnaire:
            await db_commands.delete_user_answers(respondent_id=call.from_user.id, qe_id=qe_id)  # !!!
            await db_commands.delete_user_passed_qe(respondent_id=call.from_user.id, qe_id=qe_id)
            await db_commands.decrease_passed_by(qe_id=qe_id)

            await db_commands.increase_link_clicks(creator_id=questionnaire.creator_id)
            questions = await db_commands.select_questions(qe_id=qe_id)
            question = questions[0]

            if question.question_type == "open":
                await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                                 text=f"🔍 Вы начали прохождение опроса: {questionnaire.title}\n"
                                                      f"❓ 1-й вопрос: {quote_html(question.question_text)}")
                await PassQe.OpenAnswer.set()
            else:
                answer_options = await db_commands.select_answer_options(question_id=question.question_id)
                text = await parse_answer_options(answer_options=answer_options)
                keyboard = parse_answer_options_kb(options_quantity=len(answer_options))
                await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                                 text=f"🔍 Вы начали прохождение опроса: {questionnaire.title}\n"
                                                      f"❓ 1-й вопрос: {quote_html(question.question_text)}\n\n{text}",
                                                 reply_markup=keyboard)
                await state.update_data(question_id=question.question_id)
                await PassQe.ClosedAnswer.set()

            answer_start_time = time.time()
            await state.update_data(qe_id=questionnaire.qe_id, counter=0, answer_start_time=answer_start_time,
                                    answers_quantity=questionnaire.questions_quantity, completion_time=0)
        else:
            await call.message.answer("🚫 Опрос не найден.", reply_markup=main_menu_kb)


def register_bot_start(dp: Dispatcher):
    dp.register_message_handler(deeplink_bot_start, CommandStart(deep_link=re.compile(r"^[a-zA-Z0-9]{1,10}$")),
                                state="*")
    dp.register_message_handler(bot_start, CommandStart(), state="*")
    dp.register_callback_query_handler(pass_qe_approve, pass_qe_approve_callback.filter(approve=pass_qe_approves),
                                       state=PassQe.PassBeginApprove)
    dp.register_callback_query_handler(replay_qe_approve, replay_qe_approve_callback.filter(approve=replay_approves),
                                       state=PassQe.PassReplayApprove)
