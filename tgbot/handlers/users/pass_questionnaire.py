import time

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import quote_html

from tgbot.keyboards.qe_reply_kbs import main_menu_kb
from tgbot.keyboards.qe_inline_kbs import parse_answer_options_kb, answers_approve_kb, \
    answer_options_callback, answers_approve_callback, answers_approves
from tgbot.misc.states import PassQe
from tgbot.services.database import db_commands
from tgbot.misc.dependences import USER_ANSWER_ID_LENGTH, ANSWER_LENGTH
from tgbot.services.service_functions import parse_answers_text, parse_answer_options, generate_random_id


async def get_open_answer(message: types.Message, state: FSMContext):
    if len(message.text) > ANSWER_LENGTH:
        await message.answer(f"❗ <b>Длина</b> ответа должна составлять не более <b>{ANSWER_LENGTH}</b> символов. "
                             "Введите ответ снова:")
        return

    else:
        data = await state.get_data()
        qe_id = data.get("qe_id")
        answer_start_time = data.get("answer_start_time")

        answer_id = generate_random_id(length=USER_ANSWER_ID_LENGTH)
        answer_time = time.time() - answer_start_time
        await db_commands.create_user_answer(answer_id=answer_id, qe_id=qe_id, respondent_id=message.from_user.id,
                                             answer_text=message.text, answer_time=answer_time)
        completion_time = data.get("completion_time")
        completion_time += answer_time

        counter = data.get("counter")
        answers_quantity = data.get("answers_quantity")

        counter += 1
        if counter < answers_quantity:
            await state.update_data(counter=counter)
            questions = await db_commands.select_questions(qe_id=qe_id)
            question = questions[counter]

            if question.question_type == "open":
                if question.question_photo_id:
                    if question.question_text:
                        caption = f"❓ {counter + 1}-й вопрос: {quote_html(question.question_text)}"
                    else:
                        caption = f"❓ {counter + 1}-й вопрос: описание отсутствует"
                    await message.answer_photo(photo=question.question_photo_id, caption=caption)
                else:
                    await message.answer(f"❓ {counter + 1}-й вопрос: {quote_html(question.question_text)}")
                await PassQe.OpenAnswer.set()
            else:
                answer_options = await db_commands.select_answer_options(question_id=question.question_id)
                text = await parse_answer_options(answer_options=answer_options)
                keyboard = parse_answer_options_kb(options_quantity=len(answer_options))
                if question.question_photo_id:
                    if question.question_text:
                        caption = f"❓ {counter + 1}-й вопрос: {quote_html(question.question_text)}\n\n{text}"
                    else:
                        caption = f"❓ {counter + 1}-й вопрос: описание отсутствует"
                    await message.answer_photo(photo=question.question_photo_id, caption=caption, reply_markup=keyboard)
                else:
                    await message.answer(f"❓ {counter + 1}-й вопрос: {quote_html(question.question_text)}\n\n{text}",
                                         reply_markup=keyboard)

                await PassQe.ClosedAnswer.set()
                await state.update_data(question_id=question.question_id)

            await state.update_data(answer_start_time=time.time(), completion_time=completion_time)

        else:
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
        await state.reset_data()
        await state.finish()
    else:
        answer_id = generate_random_id(length=USER_ANSWER_ID_LENGTH)
        question_id = data.get("question_id")
        answer_options = await db_commands.select_answer_options(question_id=question_id)
        position = int(answer[1])

        answer_text = answer_options[position].answer_option_text

        answer_start_time = data.get("answer_start_time")
        answer_time = time.time() - answer_start_time

        completion_time = data.get("completion_time")
        completion_time += answer_time

        await db_commands.create_user_answer(answer_id=answer_id, qe_id=qe_id, respondent_id=call.from_user.id,
                                             answer_text=answer_text, answer_time=answer_time)
        counter = data.get("counter")
        answers_quantity = data.get("answers_quantity")

        previous_question = await db_commands.select_question(question_id=question_id)
        answer_options = await db_commands.select_answer_options(question_id=question_id)
        text = (f"❓ {counter + 1}-й вопрос: {quote_html(previous_question.question_text)}\n\n"
                f"{(await parse_answer_options(answer_options))[:-19]}")

        if previous_question.question_photo_id:
            await call.bot.edit_message_caption(chat_id=call.from_user.id, message_id=call.message.message_id,
                                                caption=text)
        else:
            await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                             text=text, reply_markup=None)

        counter += 1
        if counter < answers_quantity:
            await state.update_data(counter=counter)

            questions = await db_commands.select_questions(qe_id=qe_id)
            question = questions[counter]

            if question.question_type == "open":
                if question.question_photo_id:
                    if question.question_text:
                        caption = f"❓ {counter + 1}-й вопрос: {quote_html(question.question_text)}"
                    else:
                        caption = f"❓ {counter + 1}-й вопрос: описание отсутствует"
                    await call.message.answer_photo(photo=question.question_photo_id, caption=caption)
                else:
                    await call.message.answer(f"❓ {counter + 1}-й вопрос: {quote_html(question.question_text)}")
                await PassQe.OpenAnswer.set()
            else:
                answer_options = await db_commands.select_answer_options(question_id=question.question_id)
                answer_options_text = await parse_answer_options(answer_options=answer_options)
                keyboard = parse_answer_options_kb(options_quantity=len(answer_options))
                if question.question_photo_id:
                    if question.question_text:
                        caption = (f"❓ {counter + 1}-й вопрос: {quote_html(question.question_text)}\n"
                                   f"\n{answer_options_text}")
                    else:
                        caption = f"❓ {counter + 1}-й вопрос: описание отсутствует"
                    await call.message.answer_photo(photo=question.question_photo_id, caption=caption,
                                                    reply_markup=keyboard)
                else:
                    await call.message.answer(f"❓ {counter + 1}-й вопрос: {quote_html(question.question_text)}\n\n"
                                              f"{answer_options_text}", reply_markup=keyboard)
                await PassQe.ClosedAnswer.set()
                await state.update_data(question_id=question.question_id)

            await state.update_data(answer_start_time=time.time(), completion_time=completion_time)
        else:
            await state.update_data(completion_time=completion_time)
            text = "❇️ Опрос пройден.\n\n"
            answers = await db_commands.select_user_answers(respondent_id=call.from_user.id, qe_id=qe_id)
            text += await parse_answers_text(answers=answers, answers_quantity=answers_quantity)
           # await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            await call.message.answer(text=text, reply_markup=answers_approve_kb)
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
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text="📮 Ваши ответы отправлены автору опроса.")

        user = await db_commands.select_user(id=call.from_user.id)
        if user.passed_qe_quantity % 5 == 0 and user.passed_qe_quantity != 0:
            await call.answer(f"🎉 Отлично, Вы прошли уже {user.passed_qe_quantity} опросов!", show_alert=True)

        await call.message.answer("Главное меню:", reply_markup=main_menu_kb)

    elif approve == "delete":
        await db_commands.delete_user_answers(respondent_id=call.from_user.id, qe_id=qe_id)
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text="❌ Ваши ответы удалены.")
        await call.message.answer("Главное меню:", reply_markup=main_menu_kb)

    await state.reset_data()
    await state.finish()


def register_pass_questionnaire(dp: Dispatcher):
    dp.register_message_handler(get_open_answer, content_types=types.ContentType.TEXT, state=PassQe.OpenAnswer)
    dp.register_callback_query_handler(get_closed_answer, answer_options_callback.filter(), state=PassQe.ClosedAnswer)
    dp.register_callback_query_handler(answers_approve, answers_approve_callback.filter(approve=answers_approves),
                                       state=PassQe.PassEndApprove)
