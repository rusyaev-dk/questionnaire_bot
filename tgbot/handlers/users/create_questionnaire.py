from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from tgbot.keyboards.default.qe_text_keyboards import cancel_fill_qe, main_menu_kb
from tgbot.keyboards.inline.qe_inline_keyboards import questionnaire_approve_kb, question_type_kb, share_link_kb, \
    question_type_callback, question_types, qe_approve_callback, qe_approves
from tgbot.misc.states import CreateQe
from tgbot.services.database import db_commands
from tgbot.services.dependences import MAX_QUESTIONS_QUANTITY, QUEST_ID_LENGTH, MAX_ANSWERS_QUANTITY, BOT_USERNAME
from tgbot.services.service_functions import get_rand_id, parse_questions_text


async def get_qe_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("❓ Введите <b>количество</b> вопросов:", reply_markup=cancel_fill_qe)
    await CreateQe.Questions_qty.set()


async def get_questions_quantity(message: types.Message, state: FSMContext):
    data = await state.get_data()
    title = data.get("title")
    while True:
        try:
            if message.text == "❌ Отмена":
                try:
                    quest_id = data.get("quest_id")
                    await db_commands.delete_questionnaire(quest_id=quest_id)
                    await db_commands.remove_user_created_qe(creator_id=message.from_user.id, quest_id=quest_id)
                except AttributeError:
                    pass
                await state.finish()
                await message.answer("❌ Создание опроса отменено.\nГлавное меню:", reply_markup=main_menu_kb)
                break

            questions_quantity = int(message.text)

            if questions_quantity <= 0:
                await message.answer("❗️ Введите корректное значение.")
                return
            elif questions_quantity > MAX_QUESTIONS_QUANTITY:
                await message.answer("❗️ Опрос может состоять не более чем из 15 вопросов. Введите значение снова:")
                return
            else:
                quest_id = get_rand_id(QUEST_ID_LENGTH)
                await state.update_data(quest_id=quest_id, questions_quantity=questions_quantity, counter=0)
                await db_commands.create_questionnaire(quest_id=quest_id, creator_id=message.from_user.id, title=title,
                                                       questions_quantity=questions_quantity)
                await message.answer("📍 Укажите тип 1-го вопроса:", reply_markup=question_type_kb)
                await CreateQe.QuestionType.set()
                break
        except ValueError:
            await message.answer("❗️ Введите целочисленное значение.")
            return


async def select_question_type(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    question_type = callback_data.get("question_type")
    data = await state.get_data()
    counter = data.get("counter")
    if question_type == "text":
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text=f"🔍 Введите {counter + 1}-й вопрос:")
        await CreateQe.OpenQuestionText.set()
    elif question_type == "test":
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text=f"🔍 Введите {counter + 1}-й вопрос:")
        await CreateQe.ClosedQuestionText.set()
    elif question_type == "cancel":
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await state.finish()
        await call.message.answer("❌ Создание опроса отменено.\nГлавное меню:", reply_markup=main_menu_kb)


async def get_open_question_text(message: types.Message, state: FSMContext):
    open_question = ["open", message.text]

    data = await state.get_data()
    quest_id = data.get("quest_id")
    counter = data.get("counter")
    questions_quantity = data.get("questions_quantity")

    await db_commands.add_question(quest_id=quest_id, question=open_question)
    counter += 1

    if counter < questions_quantity:
        await state.update_data(counter=counter)
        await message.answer(f"📍 Укажите тип {counter + 1}-го вопроса:", reply_markup=question_type_kb)
        await CreateQe.QuestionType.set()
    else:
        questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
        text = await parse_questions_text(questionnaire=questionnaire)
        await message.answer(text, reply_markup=questionnaire_approve_kb)
        await CreateQe.Approve.set()


async def get_closed_question_text(message: types.Message, state: FSMContext):
    closed_question = ["closed", message.text]

    data = await state.get_data()
    quest_id = data.get("quest_id")

    await db_commands.add_question(quest_id=quest_id, question=closed_question)

    await message.answer("📌 Введите <b>количество</b> вариантов <b>ответа</b>:")
    await CreateQe.ClosedAnswersQuantity.set()


async def get_closed_answers_quantity(message: types.Message, state: FSMContext):
    while True:
        try:
            answers_quantity = int(message.text)
            if answers_quantity <= 0:
                await message.answer("❗️ Введите корректное значение.")
                return
            elif answers_quantity > MAX_ANSWERS_QUANTITY:
                await message.answer("❗️ Вариантов ответа может быть не более 5. Введите значение снова:")
                return
            else:
                closed_counter = 0
                answer_options = []
                await state.update_data(answers_quantity=answers_quantity, closed_counter=closed_counter,
                                        answer_options=answer_options)
                await message.answer("📌 Введите 1-й вариант ответа:")
                await CreateQe.ClosedAnswerText.set()
                break
        except ValueError:
            await message.answer("❗️ Введите целочисленное значение.")
            return


async def get_closed_answer_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    closed_counter = data.get("closed_counter")
    answer_options = data.get("answer_options")
    answers_quantity = data.get("answers_quantity")

    while True:
        answer_options.append(message.text)
        await state.update_data(answer_options=answer_options)
        closed_counter += 1

        if closed_counter < answers_quantity:
            await message.answer(f"📌 Введите {closed_counter + 1}-й вариант ответа:")
            await state.update_data(closed_counter=closed_counter)
            return
        else:
            quest_id = data.get("quest_id")
            counter = data.get("counter")
            questions_quantity = data.get("questions_quantity")

            await db_commands.add_closed_answers(quest_id=quest_id, answers=answer_options)
            counter += 1
            if counter < questions_quantity:
                await message.answer(f"📍 Закрытый вопрос добавлен. Укажите тип {counter + 1}-го вопроса:",
                                     reply_markup=question_type_kb)
                await state.update_data(counter=counter)
                await CreateQe.QuestionType.set()
            else:
                questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
                text = await parse_questions_text(questionnaire=questionnaire)
                await message.answer(text, reply_markup=questionnaire_approve_kb)
                await CreateQe.Approve.set()
            break


async def approve_questionnaire(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    approve = callback_data.get("approve")
    data = await state.get_data()
    quest_id = data.get("quest_id")
    if approve == "create":
        await db_commands.add_user_created_qe(creator_id=call.from_user.id, quest_id=quest_id)
        await state.finish()
        link = f"https://t.me/{BOT_USERNAME}/?start={quest_id}"
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text="✅ Отлично, Ваш опрос добавлен в базу данных "
                                         "и доступен для прохождения другими пользователями.\n\n"
                                         f"📎 Ссылка для прохождения: <b>{link}</b>",
                                         reply_markup=share_link_kb(link))
        await call.message.answer("Главное меню:", reply_markup=main_menu_kb)
    elif approve == "delete":
        await db_commands.delete_questionnaire(quest_id=quest_id)
        await state.finish()
        await call.message.answer("❌ Создание опроса отменено. Главное меню:",
                                  reply_markup=main_menu_kb)


def register_create_questionnaire(dp: Dispatcher):
    text = types.ContentType.TEXT
    dp.register_message_handler(get_qe_title, content_types=text, state=CreateQe.Title)
    dp.register_message_handler(get_questions_quantity, content_types=text, state=CreateQe.Questions_qty)
    dp.register_callback_query_handler(select_question_type, question_type_callback.filter(question_type=question_types),
                                       state=CreateQe.QuestionType)

    dp.register_message_handler(get_open_question_text, content_types=text, state=CreateQe.OpenQuestionText)
    dp.register_message_handler(get_closed_question_text, content_types=text, state=CreateQe.ClosedQuestionText)
    dp.register_message_handler(get_closed_answers_quantity, content_types=text, state=CreateQe.ClosedAnswersQuantity)
    dp.register_message_handler(get_closed_answer_text, content_types=text, state=CreateQe.ClosedAnswerText)

    dp.register_callback_query_handler(approve_questionnaire, qe_approve_callback.filter(approve=qe_approves),
                                       state=CreateQe.Approve)
