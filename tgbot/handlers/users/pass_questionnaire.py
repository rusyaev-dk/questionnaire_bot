from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from tgbot.keyboards.default.qe_text_keyboards import main_menu_kb
from tgbot.keyboards.inline.qe_inline_keyboards import generate_answer_options, answers_approve_kb, \
    answer_options_callback, answers_approve_callback, answers_approves
from tgbot.misc.states import FillQe
from tgbot.services.database import db_commands
from tgbot.services.service_functions import parse_answers_text, parse_answer_options


async def get_open_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    quest_id = data.get("quest_id")
    await db_commands.add_qe_answer(quest_id=quest_id, respondent_id=message.from_user.id, answer=message.text)

    counter = data.get("counter")
    answers_quantity = data.get("answers_quantity")
    counter += 1

    if counter < answers_quantity:
        await state.update_data(counter=counter)
        questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
        questions = questionnaire.questions
        if questions[counter][0] == "open":
            await message.answer(f"❓ {counter + 1}-й вопрос: {questionnaire.questions[counter][1]}")
            await FillQe.OpenAnswer.set()
        else:
            closed_counter = data.get("closed_counter")
            answers_list = questionnaire.answer_options  # two-dimensional list
            answer_options = answers_list[closed_counter]
            text = await parse_answer_options(answer_options=answer_options)
            await message.answer(f"❓ {counter + 1}-й вопрос: {questionnaire.questions[counter][1]}\n\n{text}",
                                 reply_markup=generate_answer_options(answers_quantity=len(answer_options)))
            await state.update_data(closed_counter=closed_counter + 1)
            await FillQe.ClosedAnswer.set()
    else:
        respondent_answers = await db_commands.select_qe_answers(quest_id=quest_id, respondent_id=message.from_user.id)
        text = "❇️ Опрос пройден.\n\n"
        text += await parse_answers_text(answers=respondent_answers.answers)
        await message.answer(text, reply_markup=answers_approve_kb)
        await FillQe.Approve.set()


async def get_closed_answer(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    answer = callback_data.get("answer")
    if answer == "cancel":
        await call.answer("!!!!")
    else:
        data = await state.get_data()
        quest_id = data.get("quest_id")
        await db_commands.add_qe_answer(quest_id=quest_id, respondent_id=call.from_user.id, answer=answer)

        counter = data.get("counter")
        answers_quantity = data.get("answers_quantity")
        counter += 1

        if counter < answers_quantity:
            await state.update_data(counter=counter)
            questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
            questions = questionnaire.questions

            if questions[counter][0] == "open":
                await call.message.answer(f"❓ {counter + 1}-й вопрос: {questionnaire.questions[counter][1]}")
                await FillQe.OpenAnswer.set()
            else:
                closed_counter = data.get("closed_counter")
                answers_list = questionnaire.answer_options  # two-dimensional list
                answer_options = answers_list[closed_counter]
                text = await parse_answer_options(answer_options=answer_options)

                await call.message.answer(f"❓ {counter + 1}-й вопрос: {questionnaire.questions[counter][1]}\n\n{text}",
                                          reply_markup=generate_answer_options(answers_quantity=len(answer_options)))
                await state.update_data(closed_counter=closed_counter + 1)
                await FillQe.ClosedAnswer.set()
        else:
            respondent_answers = await db_commands.select_qe_answers(quest_id=quest_id, respondent_id=call.from_user.id)
            text = "❇️ Опрос пройден.\n\n"
            text += await parse_answers_text(answers=respondent_answers.answers)
            await call.message.answer(text, reply_markup=answers_approve_kb)
            await FillQe.Approve.set()


async def approve_answers(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    approve = callback_data.get("approve")
    data = await state.get_data()
    quest_id = data.get("quest_id")
    if approve == "send":
        await db_commands.add_user_passed_qe(quest_id=quest_id, respondent_id=call.from_user.id)
        await db_commands.update_complete_status(quest_id=quest_id, respondent_id=call.from_user.id, status="true")
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.message.answer("📮 Ваши ответы отправлены создателю опроса.",
                                  reply_markup=main_menu_kb)
        await state.finish()
    elif approve == "delete":
        await db_commands.delete_qe_answers_field(quest_id=quest_id, respondent_id=call.from_user.id)
        await call.message.answer("❌ Ваши ответы удалены",
                                  reply_markup=main_menu_kb)
        await state.finish()


def register_pass_questionnaire(dp: Dispatcher):
    text = types.ContentType.TEXT
    dp.register_message_handler(get_open_answer, content_types=text, state=FillQe.OpenAnswer)
    dp.register_callback_query_handler(get_closed_answer, answer_options_callback.filter(), state=FillQe.ClosedAnswer)
    dp.register_callback_query_handler(approve_answers, answers_approve_callback.filter(approve=answers_approves),
                                       state=FillQe.Approve)
