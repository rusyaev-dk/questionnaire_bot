from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from tgbot.keyboards.qe_reply_kbs import main_menu_kb
from tgbot.keyboards.qe_inline_kbs import questionnaire_approve_kb, question_type_kb, share_link_kb, \
    question_type_callback, question_types, qe_approve_callback, qe_approves
from tgbot.misc.states import CreateQe
from tgbot.services.database import db_commands
from tgbot.misc.dependences import MAX_QUESTIONS_QUANTITY, QE_ID_LENGTH, MAX_ANSWERS_QUANTITY, \
    QUESTION_ID_LENGTH, ANSWER_OPTION_ID_LENGTH, TITLE_LENGTH, QUESTION_LENGTH, ANSWER_OPTION_LENGTH
from tgbot.services.service_functions import generate_random_id, parse_questions_text, parse_share_link


async def get_qe_title(message: types.Message, state: FSMContext):
    if len(message.text) > TITLE_LENGTH:
        await message.answer(f"❗ <b>Длина</b> названия должна составлять не более <b>{TITLE_LENGTH}</b> символов. "
                             "Введите название снова:")
        return

    elif ">" in message.text or "<" in message.text:
        await message.answer("❗️ Пожалуйста, не используйте символы \"<\" и \">\".", parse_mode='Markdown')
        return

    else:
        await state.update_data(title=message.text)
        await message.answer("🔸 Введите <b>количество</b> вопросов:")
        await CreateQe.QuestionsQuantity.set()


async def get_questions_quantity(message: types.Message, state: FSMContext):
    try:
        questions_quantity = int(message.text)
        if questions_quantity <= 0:
            await message.answer("❗️ Введите корректное значение.")
            return

        elif questions_quantity > MAX_QUESTIONS_QUANTITY:
            await message.answer(f"❗️ Опрос может состоять не более чем из {MAX_QUESTIONS_QUANTITY} вопросов. "
                                 f"Введите количество снова:")
            return

        else:
            data = await state.get_data()
            title = data.get("title")
            qe_id = generate_random_id(QE_ID_LENGTH)

            await db_commands.create_questionnaire(qe_id=qe_id, creator_id=message.from_user.id, title=title,
                                                   questions_quantity=questions_quantity)
            await state.update_data(qe_id=qe_id, questions_quantity=questions_quantity, counter=0)

            await message.answer("📍 Укажите тип 1-го вопроса:", reply_markup=question_type_kb)
            await CreateQe.QuestionType.set()
    except ValueError:
        await message.answer("❗️ Введите целочисленное значение.")
        return


async def select_question_type(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    question_type = callback_data.get("question_type")
    data = await state.get_data()
    counter = data.get("counter")
    if question_type == "open":
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text=f"❓ Введите {counter + 1}-й вопрос:")
        await state.update_data(question_type="open")
        await CreateQe.QuestionText.set()

    elif question_type == "closed":
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text=f"❓ Введите {counter + 1}-й вопрос:")
        await state.update_data(question_type="closed")
        await CreateQe.QuestionText.set()

    elif question_type == "cancel":
        qe_id = data.get("qe_id")
        await db_commands.delete_questionnaire(qe_id=qe_id)
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text="❌ Создание опроса отменено.")
        await call.message.answer("Главное меню:", reply_markup=main_menu_kb)
        await state.reset_data()
        await state.finish()


async def get_question_text(message: types.Message, state: FSMContext):
    if len(message.text) > QUESTION_LENGTH:
        await message.answer(f"❗ <b>Длина</b> вопроса должна составлять не более <b>{QUESTION_LENGTH}</b> символов. "
                             "Введите вопрос снова:")
        return

    elif ">" in message.text or "<" in message.text:
        await message.answer("❗️ Пожалуйста, не используйте символы \"<\" и \">\".", parse_mode='Markdown')
        return

    else:
        data = await state.get_data()
        qe_id = data.get("qe_id")
        counter = data.get("counter")
        questions_quantity = data.get("questions_quantity")

        question_type = data.get("question_type")
        question_id = generate_random_id(length=QUESTION_ID_LENGTH)
        await state.update_data(question_id=question_id)
        await db_commands.create_question(question_id=question_id, qe_id=qe_id, question_type=question_type,
                                          question_text=message.text)
        if question_type == "open":
            counter += 1
            if counter < questions_quantity:
                await state.update_data(counter=counter)
                await message.answer(f"📍 Укажите тип {counter + 1}-го вопроса:", reply_markup=question_type_kb)
                await CreateQe.QuestionType.set()
            else:
                questionnaire = await db_commands.select_questionnaire(qe_id=qe_id)
                text = await parse_questions_text(questionnaire=questionnaire)
                await message.answer(text, reply_markup=questionnaire_approve_kb)
                await CreateQe.CreateApprove.set()
        else:
            await message.answer("🔸 Введите <b>количество</b> вариантов <b>ответа</b>:")
            await CreateQe.AnswerOptionsQuantity.set()


async def get_closed_answers_quantity(message: types.Message, state: FSMContext):
    try:
        answers_quantity = int(message.text)
        if answers_quantity <= 0:
            await message.answer("❗️ Введите корректное значение.")
            return

        elif answers_quantity > MAX_ANSWERS_QUANTITY:
            await message.answer("❗️ Вариантов ответа может быть не более 5. Введите количество снова:")
            return

        else:
            closed_counter = 0
            await state.update_data(answers_quantity=answers_quantity, closed_counter=closed_counter)
            await message.answer("📌 Введите 1-й вариант ответа:")
            await CreateQe.AnswerOptionText.set()

    except ValueError:
        await message.answer("❗️ Введите целочисленное значение.")
        return


async def get_closed_answer_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    closed_counter = data.get("closed_counter")
    answers_quantity = data.get("answers_quantity")
    question_id = data.get("question_id")

    if len(message.text) > ANSWER_OPTION_LENGTH:
        await message.answer(f"❗ <b>Длина</b> варианта ответа должна составлять не более <b>{ANSWER_OPTION_LENGTH}</b> "
                             f"символов. Введите вариант ответа снова:")
        return

    elif ">" in message.text or "<" in message.text:
        await message.answer("❗️ Пожалуйста, не используйте символы \"<\" и \">\".", parse_mode='Markdown')
        return

    else:
        answer_option_id = generate_random_id(length=ANSWER_OPTION_ID_LENGTH)
        await db_commands.create_answer_option(answer_option_id=answer_option_id, question_id=question_id,
                                               answer_option_text=message.text)

        closed_counter += 1
        if closed_counter < answers_quantity:
            await message.answer(f"📌 Введите {closed_counter + 1}-й вариант ответа:")
            await state.update_data(closed_counter=closed_counter)
            return
        else:
            qe_id = data.get("qe_id")
            counter = data.get("counter")
            questions_quantity = data.get("questions_quantity")

            counter += 1
            if counter < questions_quantity:
                await message.answer(f"✅ Закрытый вопрос добавлен. Укажите тип {counter + 1}-го вопроса:",
                                     reply_markup=question_type_kb)
                await state.update_data(counter=counter)
                await CreateQe.QuestionType.set()
            else:
                questionnaire = await db_commands.select_questionnaire(qe_id=qe_id)
                text = await parse_questions_text(questionnaire=questionnaire)
                await message.answer(text, reply_markup=questionnaire_approve_kb)
                await CreateQe.CreateApprove.set()


async def questionnaire_approve(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    approve = callback_data.get("approve")
    data = await state.get_data()
    qe_id = data.get("qe_id")
    if approve == "create":
        await db_commands.add_created_qe(creator_id=call.from_user.id, qe_id=qe_id)
        await db_commands.increase_user_created_qe_quantity(creator_id=call.from_user.id)
        link = await parse_share_link(qe_id=qe_id)
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text="✅ Отлично, Ваш опрос добавлен в базу данных "
                                         "и доступен для прохождения другими пользователями.\n\n"
                                         f"📎 Ссылка для прохождения: <b>{link}</b>",
                                         reply_markup=share_link_kb(link), disable_web_page_preview=True)
        await call.message.answer("Главное меню:", reply_markup=main_menu_kb)
        await state.reset_data()
        await state.finish()
    elif approve == "delete":
        await db_commands.delete_questionnaire(qe_id=qe_id)
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text="❌ Создание опроса отменено.")
        await call.message.answer("Главное меню:",
                                  reply_markup=main_menu_kb)
        await state.reset_data()
        await state.finish()


def register_create_questionnaire(dp: Dispatcher):
    text = types.ContentType.TEXT
    dp.register_message_handler(get_qe_title, content_types=text, state=CreateQe.Title)
    dp.register_message_handler(get_questions_quantity, content_types=text, state=CreateQe.QuestionsQuantity)
    dp.register_callback_query_handler(select_question_type, question_type_callback.filter(question_type=question_types),
                                       state=CreateQe.QuestionType)

    dp.register_message_handler(get_question_text, content_types=text, state=CreateQe.QuestionText)
    dp.register_message_handler(get_closed_answers_quantity, content_types=text, state=CreateQe.AnswerOptionsQuantity)
    dp.register_message_handler(get_closed_answer_text, content_types=text, state=CreateQe.AnswerOptionText)

    dp.register_callback_query_handler(questionnaire_approve, qe_approve_callback.filter(approve=qe_approves),
                                       state=CreateQe.CreateApprove)
