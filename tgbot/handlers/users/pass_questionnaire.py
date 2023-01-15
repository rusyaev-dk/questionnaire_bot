import time

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from tgbot.keyboards.default.qe_text_keyboards import main_menu_kb
from tgbot.keyboards.inline.qe_inline_keyboards import parse_answer_options_kb, answers_approve_kb, \
    answer_options_callback, answers_approve_callback, answers_approves
from tgbot.misc.states import PassQe
from tgbot.services.database import db_commands
from tgbot.misc.dependences import USER_ANSWER_ID_LENGTH, ANSWER_LENGTH
from tgbot.services.service_functions import parse_answers_text, parse_answer_options, generate_random_id


async def get_open_answer(message: types.Message, state: FSMContext):
    while True:
        if len(message.text) > ANSWER_LENGTH:
            await message.answer(f"❗ <b>Длина</b> ответа должна составлять не более <b>{ANSWER_LENGTH}</b> символов. "
                                 "Введите ответ снова:")
            return
        else:
            data = await state.get_data()
            qe_id = data.get("qe_id")
            answer_id = generate_random_id(length=USER_ANSWER_ID_LENGTH)
            await db_commands.create_user_answer(answer_id=answer_id, qe_id=qe_id, respondent_id=message.from_user.id,
                                                 answer_text=message.text)
            break

    counter = data.get("counter")
    answers_quantity = data.get("answers_quantity")
    counter += 1

    if counter < answers_quantity:
        await state.update_data(counter=counter)
        questions = await db_commands.select_questions(qe_id=qe_id)
        question = questions[counter]

        if question.question_type == "open":
            await message.answer(f"❓ {counter + 1}-й вопрос: {question.question_text}")
            await PassQe.OpenAnswer.set()
        else:
            answer_options = await db_commands.select_answer_options(question_id=question.question_id)
            text = await parse_answer_options(answer_options=answer_options)
            await message.answer(f"❓ {counter + 1}-й вопрос: {question.question_text}\n\n{text}",
                                 reply_markup=parse_answer_options_kb(options_quantity=len(answer_options)))
            await PassQe.ClosedAnswer.set()
    else:
        start_time = data.get("start_time")
        completion_time = time.time() - start_time
        await state.update_data(completion_time=completion_time)

        text = "❇️ Опрос пройден.\n\n"
        answers = await db_commands.select_user_answers(respondent_id=message.from_user.id, qe_id=qe_id)
        text += await parse_answers_text(answers=answers, answers_quantity=answers_quantity)
        await message.answer(text, reply_markup=answers_approve_kb)
        await PassQe.PassEndApprove.set()


async def get_closed_answer(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    answer = callback_data.get("answer")
    data = await state.get_data()
    qe_id = data.get("qe_id")
    if answer == "cancel":
        await db_commands.delete_user_answers(respondent_id=call.from_user.id, qe_id=qe_id)
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text="❌ Прохождение опроса отменено.")
        await call.message.answer("Главное меню:", reply_markup=main_menu_kb)
        await state.finish()
    else:

        answer_id = generate_random_id(length=USER_ANSWER_ID_LENGTH)
        await db_commands.create_user_answer(answer_id=answer_id, qe_id=qe_id, respondent_id=call.from_user.id,
                                             answer_text=answer)
        counter = data.get("counter")
        answers_quantity = data.get("answers_quantity")
        counter += 1

        if counter < answers_quantity:
            await state.update_data(counter=counter)
            questions = await db_commands.select_questions(qe_id=qe_id)
            question = questions[counter]

            if question.question_type == "open":
                await call.message.answer(f"❓ {counter + 1}-й вопрос: {question.question_text}")
                await PassQe.OpenAnswer.set()
            else:
                answer_options = await db_commands.select_answer_options(question_id=question.question_id)
                text = await parse_answer_options(answer_options=answer_options)
                await call.message.answer(f"❓ {counter + 1}-й вопрос: {question.question_text}\n\n{text}",
                                          reply_markup=parse_answer_options_kb(options_quantity=len(answer_options)))
                await PassQe.ClosedAnswer.set()
        else:
            start_time = data.get("start_time")
            completion_time = time.time() - start_time
            await state.update_data(completion_time=completion_time)

            text = "❇️ Опрос пройден.\n\n"
            answers = await db_commands.select_user_answers(respondent_id=call.from_user.id, qe_id=qe_id)
            text += await parse_answers_text(answers=answers, answers_quantity=answers_quantity)
            await call.message.answer(text, reply_markup=answers_approve_kb)
            await PassQe.PassEndApprove.set()


async def answers_approve(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    approve = callback_data.get("approve")
    data = await state.get_data()
    qe_id = data.get("qe_id")
    if approve == "send":
        completion_time = data.get("completion_time")
        await db_commands.add_passed_qe(respondent_id=call.from_user.id, qe_id=qe_id, completion_time=completion_time)
        await db_commands.increase_qe_passed_by(qe_id=qe_id)
        await db_commands.increase_user_passed_qe_quantity(respondent_id=call.from_user.id)
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.message.answer("📮 Ваши ответы отправлены автору опроса.",
                                  reply_markup=main_menu_kb)
        await state.finish()
    elif approve == "delete":
        await db_commands.delete_user_answers(respondent_id=call.from_user.id, qe_id=qe_id)
        await call.message.answer("❌ Ваши ответы удалены.",
                                  reply_markup=main_menu_kb)
        await state.finish()


def register_pass_questionnaire(dp: Dispatcher):
    text = types.ContentType.TEXT
    dp.register_message_handler(get_open_answer, content_types=text, state=PassQe.OpenAnswer)
    dp.register_callback_query_handler(get_closed_answer, answer_options_callback.filter(), state=PassQe.ClosedAnswer)
    dp.register_callback_query_handler(answers_approve, answers_approve_callback.filter(approve=answers_approves),
                                       state=PassQe.PassEndApprove)
