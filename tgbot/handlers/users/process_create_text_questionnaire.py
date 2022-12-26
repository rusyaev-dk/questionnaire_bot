from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from tgbot.keyboards.default.base_keyboards import main_menu_kb
from tgbot.keyboards.inline.questionnaire_keyboards import questionnaire_approve_kb, q_approve_callback, q_approves
from tgbot.misc.states import CreateQE
from tgbot.services.database import db_commands
from tgbot.services.service_functions import get_rand_id, parse_questions_text


async def get_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Укажите количество вопросов:")
    await CreateQE.Questions_qty.set()


async def create_questionnaire(message: types.Message, state: FSMContext):
    data = await state.get_data()
    title = data.get("title")
    questions_quantity = int(message.text)
    quest_id = get_rand_id(10)
    await state.update_data(quest_id=quest_id)
    await state.update_data(questions_quantity=questions_quantity)
    await state.update_data(counter=1)
    await db_commands.create_questionnaire(quest_id=quest_id, creator_id=message.from_user.id, title=title,
                                           questions_quantity=questions_quantity)
    await message.answer("Введите 1 вопрос:")
    await CreateQE.Q1.set()


async def get_1_question_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    quest_id = data.get("quest_id")
    counter = data.get("counter")
    questions_quantity = data.get("questions_quantity")
    await db_commands.add_question(quest_id=quest_id, question=message.text)
    if counter < questions_quantity:
        await message.answer(f"Введите 2 вопрос:")
        counter += 1
        await state.update_data(counter=counter)
        await CreateQE.Q2.set()
    else:
        questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
        text = await parse_questions_text(questionnaire=questionnaire)
        await message.answer(text, reply_markup=questionnaire_approve_kb)
        await CreateQE.Approve.set()


async def get_2_question_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    quest_id = data.get("quest_id")
    counter = data.get("counter")
    questions_quantity = data.get("questions_quantity")
    await db_commands.add_question(quest_id=quest_id, question=message.text)
    if counter < questions_quantity:
        await message.answer(f"Введите 3 вопрос:")
        counter += 1
        await state.update_data(counter=counter)
        await CreateQE.Q3.set()
    else:
        questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
        text = await parse_questions_text(questionnaire=questionnaire)
        await message.answer(text, reply_markup=questionnaire_approve_kb)
        await CreateQE.Approve.set()


async def get_3_question_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    quest_id = data.get("quest_id")
    counter = data.get("counter")
    questions_quantity = data.get("questions_quantity")
    await db_commands.add_question(quest_id=quest_id, question=message.text)
    if counter < questions_quantity:
        await message.answer("Введите 4 вопрос:")
        counter += 1
        await state.update_data(counter=counter)
        await CreateQE.Q4.set()
    else:
        questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
        text = await parse_questions_text(questionnaire=questionnaire)
        await message.answer(text, reply_markup=questionnaire_approve_kb)
        await CreateQE.Approve.set()


async def get_4_question_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    quest_id = data.get("quest_id")
    counter = data.get("counter")
    questions_quantity = data.get("questions_quantity")
    await db_commands.add_question(quest_id=quest_id, question=message.text)
    if counter < questions_quantity:
        await message.answer("Введите 5 вопрос:")
        counter += 1
        await state.update_data(counter=counter)
        await CreateQE.Q5.set()
    else:
        questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
        text = await parse_questions_text(questionnaire=questionnaire)
        await message.answer(text, reply_markup=questionnaire_approve_kb)
        await CreateQE.Approve.set()


async def get_5_question_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    quest_id = data.get("quest_id")
    counter = data.get("counter")
    questions_quantity = data.get("questions_quantity")
    await db_commands.add_question(quest_id=quest_id, question=message.text)
    if counter < questions_quantity:
        await message.answer("Введите 6 вопрос:")
        counter += 1
        await state.update_data(counter=counter)
        await CreateQE.Q6.set()
    else:
        questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
        text = await parse_questions_text(questionnaire=questionnaire)
        await message.answer(text, reply_markup=questionnaire_approve_kb)
        await CreateQE.Approve.set()


async def get_6_question_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    quest_id = data.get("quest_id")
    counter = data.get("counter")
    questions_quantity = data.get("questions_quantity")
    await db_commands.add_question(quest_id=quest_id, question=message.text)
    if counter < questions_quantity:
        await message.answer("Введите 7 вопрос:")
        counter += 1
        await state.update_data(counter=counter)
        await CreateQE.Q7.set()
    else:
        questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
        text = await parse_questions_text(questionnaire=questionnaire)
        await message.answer(text, reply_markup=questionnaire_approve_kb)
        await CreateQE.Approve.set()


async def get_7_question_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    quest_id = data.get("quest_id")
    counter = data.get("counter")
    questions_quantity = data.get("questions_quantity")
    await db_commands.add_question(quest_id=quest_id, question=message.text)
    if counter < questions_quantity:
        await message.answer("Введите 8 вопрос:")
        counter += 1
        await state.update_data(counter=counter)
        await CreateQE.Q8.set()
    else:
        questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
        text = await parse_questions_text(questionnaire=questionnaire)
        await message.answer(text, reply_markup=questionnaire_approve_kb)
        await CreateQE.Approve.set()


async def get_8_question_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    quest_id = data.get("quest_id")
    counter = data.get("counter")
    questions_quantity = data.get("questions_quantity")
    await db_commands.add_question(quest_id=quest_id, question=message.text)
    if counter < questions_quantity:
        await message.answer("Введите 9 вопрос:")
        counter += 1
        await state.update_data(counter=counter)
        await CreateQE.Q9.set()
    else:
        questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
        text = await parse_questions_text(questionnaire=questionnaire)
        await message.answer(text, reply_markup=questionnaire_approve_kb)
        await CreateQE.Approve.set()


async def get_9_question_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    quest_id = data.get("quest_id")
    counter = data.get("counter")
    questions_quantity = data.get("questions_quantity")
    await db_commands.add_question(quest_id=quest_id, question=message.text)
    if counter < questions_quantity:
        await message.answer("Введите 10 вопрос:")
        counter += 1
        await state.update_data(counter=counter)
        await CreateQE.Q10.set()
    else:
        questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
        text = await parse_questions_text(questionnaire=questionnaire)
        await message.answer(text, reply_markup=questionnaire_approve_kb)
        await CreateQE.Approve.set()


async def get_10_question_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    quest_id = data.get("quest_id")
    await db_commands.add_question(quest_id=quest_id, question=message.text)
    questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
    text = await parse_questions_text(questionnaire=questionnaire)
    await message.answer(text, reply_markup=questionnaire_approve_kb)
    await CreateQE.Approve.set()


async def approve_questionnaire(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    approve = callback_data.get("approve")
    data = await state.get_data()
    quest_id = data.get("quest_id")
    if approve == "true":
        await state.finish()
        await call.message.answer("Отлично, Ваш опрос добавлен в базу данных "
                                  "и доступен для прохождения другими пользователями\n"
                                  f"Ссылка для прохождения: https://t.me/msu_talk_bot/?start={quest_id}",
                                  reply_markup=main_menu_kb)
    elif approve == "false":

        await db_commands.delete_questionnaire(creator_id=call.from_user.id, quest_id=quest_id)
        await state.finish()
        await call.message.answer("Создание опроса отменено...",
                                  reply_markup=main_menu_kb)


def register_process_questionnaire(dp: Dispatcher):
    dp.register_message_handler(get_title, content_types=types.ContentType.TEXT, state=CreateQE.Title)
    dp.register_message_handler(create_questionnaire, content_types=types.ContentType.TEXT,
                                state=CreateQE.Questions_qty)

    dp.register_message_handler(get_1_question_text, content_types=types.ContentType.TEXT, state=CreateQE.Q1)
    dp.register_message_handler(get_2_question_text, content_types=types.ContentType.TEXT, state=CreateQE.Q2)
    dp.register_message_handler(get_3_question_text, content_types=types.ContentType.TEXT, state=CreateQE.Q3)
    dp.register_message_handler(get_4_question_text, content_types=types.ContentType.TEXT, state=CreateQE.Q4)
    dp.register_message_handler(get_5_question_text, content_types=types.ContentType.TEXT, state=CreateQE.Q5)
    dp.register_message_handler(get_6_question_text, content_types=types.ContentType.TEXT, state=CreateQE.Q6)
    dp.register_message_handler(get_7_question_text, content_types=types.ContentType.TEXT, state=CreateQE.Q7)
    dp.register_message_handler(get_8_question_text, content_types=types.ContentType.TEXT, state=CreateQE.Q8)
    dp.register_message_handler(get_9_question_text, content_types=types.ContentType.TEXT, state=CreateQE.Q9)
    dp.register_message_handler(get_10_question_text, content_types=types.ContentType.TEXT, state=CreateQE.Q10)
    dp.register_callback_query_handler(approve_questionnaire, q_approve_callback.filter(approve=q_approves),
                                       state=CreateQE.Approve)