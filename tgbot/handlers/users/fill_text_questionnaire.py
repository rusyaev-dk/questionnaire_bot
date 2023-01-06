from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from tgbot.keyboards.default.qe_text_keyboards import main_menu_kb, cancel_fill_qe
from tgbot.keyboards.inline.qe_inline_keyboards import text_answers_approve_kb, text_answers_approve_callback, \
    text_a_approves
from tgbot.misc.states import FillQe
from tgbot.services.database import db_commands
from tgbot.services.service_functions import parse_answers_text


async def get_answer_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    quest_id = data.get("quest_id")
    counter = data.get("counter")
    answers_quantity = data.get("answers_quantity")
    questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
    while True:
        if message.text == "❌ Отмена":
            await db_commands.delete_qe_text_answers(quest_id=quest_id, respondent_id=message.from_user.id)
            await state.finish()
            await message.answer("❌ Прохождение опроса отменено.\nГлавное меню:", reply_markup=main_menu_kb)
            break

        await db_commands.add_text_answer(quest_id=quest_id, respondent_id=message.from_user.id, answer=message.text)
        counter += 1

        if counter < answers_quantity:
            await message.answer(f" {counter + 1}-й вопрос: {questionnaire.questions[counter]}",
                                 reply_markup=cancel_fill_qe)
            await state.update_data(counter=counter)
            return
        else:
            await FillQe.Approve.set()
            qe_text_answers = await db_commands.select_qe_text_answers(quest_id=quest_id,
                                                                       respondent_id=message.from_user.id)
            text = "📑 Опрос пройден.\n\n"
            text += await parse_answers_text(qe_text_answers=qe_text_answers)
            await message.answer(text, reply_markup=text_answers_approve_kb)
            break


async def approve_text_answers(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    approve = callback_data.get("answers_approve")
    data = await state.get_data()
    quest_id = data.get("quest_id")
    if approve == "true":
        await state.finish()
        await db_commands.add_user_passed_qe(id=call.from_user.id, quest_id=quest_id)
        await db_commands.update_complete_status(quest_id=quest_id, respondent_id=call.from_user.id, status="true")
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.message.answer("📮 Ваши ответы отправлены создателю опроса.",
                                  reply_markup=main_menu_kb)
    elif approve == "false":
        await db_commands.delete_qe_text_answers(quest_id=quest_id, respondent_id=call.from_user.id)
        await call.message.answer("❌ Ваши ответы удалены",
                                  reply_markup=main_menu_kb)
        await state.finish()


def register_fill_text_qe(dp: Dispatcher):
    dp.register_message_handler(get_answer_text, content_types=types.ContentType.TEXT, state=FillQe.GetAnswer)
    dp.register_callback_query_handler(approve_text_answers, text_answers_approve_callback.filter(
        answers_approve=text_a_approves), state=FillQe.Approve)
