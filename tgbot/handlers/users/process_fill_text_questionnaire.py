from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from tgbot.keyboards.default.base_keyboards import main_menu_kb
from tgbot.keyboards.inline.questionnaire_keyboards import text_answers_approve_kb, text_answers_approve_callback, \
    text_a_approves
from tgbot.misc.states import FillQE
from tgbot.services.database import db_commands
from tgbot.services.service_functions import parse_answers_text


async def get_1_answer_text(message: types.Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.finish()
        await message.answer("Прохождение опроса прекращено...\n"
                             "Главное меню:", reply_markup=main_menu_kb)
    else:
        data = await state.get_data()
        counter = data.get("counter")
        quest_id = data.get("quest_id")
        answers_quantity = data.get("answers_quantity")
        await db_commands.add_text_answer(quest_id=quest_id, respondent_id=message.from_user.id,
                                          answer=message.text)
        if counter < answers_quantity:
            questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
            await message.answer(f"Вопрос 2: {questionnaire.questions[counter]}")
            counter += 1
            await state.update_data(counter=counter)
            await FillQE.A2.set()
        else:
            await FillQE.Approve.set()
            qe_text_answers = await db_commands.select_qe_text_answers(quest_id=quest_id,
                                                                       respondent_id=message.from_user.id)
            text = "Отлично, Вы заполнили анкету:\n"
            text += await parse_answers_text(qe_text_answers=qe_text_answers)
            await message.answer(text, reply_markup=text_answers_approve_kb)


async def get_2_answer_text(message: types.Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.finish()
        await message.answer("Прохождение опроса прекращено...\n"
                             "Главное меню:", reply_markup=main_menu_kb)
    else:
        data = await state.get_data()
        counter = data.get("counter")
        quest_id = data.get("quest_id")
        answers_quantity = data.get("answers_quantity")
        await db_commands.add_text_answer(quest_id=quest_id, respondent_id=message.from_user.id,
                                          answer=message.text)
        if counter < answers_quantity:
            questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
            await message.answer(f"Вопрос 3: {questionnaire.questions[counter]}")
            counter += 1
            await state.update_data(counter=counter)
            await FillQE.A3.set()
        else:
            await FillQE.Approve.set()
            qe_text_answers = await db_commands.select_qe_text_answers(quest_id=quest_id,
                                                                       respondent_id=message.from_user.id)
            text = "Отлично, Вы заполнили анкету:\n"
            text += await parse_answers_text(qe_text_answers=qe_text_answers)
            await message.answer(text, reply_markup=text_answers_approve_kb)


async def get_3_answer_text(message: types.Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.finish()
        await message.answer("Прохождение опроса прекращено...\n"
                             "Главное меню:", reply_markup=main_menu_kb)
    else:
        data = await state.get_data()
        counter = data.get("counter")
        quest_id = data.get("quest_id")
        answers_quantity = data.get("answers_quantity")
        await db_commands.add_text_answer(quest_id=quest_id, respondent_id=message.from_user.id,
                                          answer=message.text)
        if counter < answers_quantity:
            questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
            await message.answer(f"Вопрос 4: {questionnaire.questions[counter]}")
            counter += 1
            await state.update_data(counter=counter)

            await FillQE.A4.set()
        else:
            await FillQE.Approve.set()
            qe_text_answers = await db_commands.select_qe_text_answers(quest_id=quest_id,
                                                                       respondent_id=message.from_user.id)
            text = "Отлично, Вы заполнили анкету:\n"
            text += await parse_answers_text(qe_text_answers=qe_text_answers)
            await message.answer(text, reply_markup=text_answers_approve_kb)


async def get_4_answer_text(message: types.Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.finish()
        await message.answer("Прохождение опроса прекращено...\n"
                             "Главное меню:", reply_markup=main_menu_kb)
    else:
        data = await state.get_data()
        counter = data.get("counter")
        quest_id = data.get("quest_id")
        answers_quantity = data.get("answers_quantity")
        await db_commands.add_text_answer(quest_id=quest_id, respondent_id=message.from_user.id,
                                          answer=message.text)
        if counter < answers_quantity:
            questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
            await message.answer(f"Вопрос 5: {questionnaire.questions[counter]}")
            counter += 1
            await state.update_data(counter=counter)

            await FillQE.A5.set()
        else:
            await FillQE.Approve.set()
            qe_text_answers = await db_commands.select_qe_text_answers(quest_id=quest_id,
                                                                       respondent_id=message.from_user.id)
            text = "Отлично, Вы заполнили анкету:\n"
            text += await parse_answers_text(qe_text_answers=qe_text_answers)
            await message.answer(text, reply_markup=text_answers_approve_kb)


async def get_5_answer_text(message: types.Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.finish()
        await message.answer("Прохождение опроса прекращено...\n"
                             "Главное меню:", reply_markup=main_menu_kb)
    else:
        data = await state.get_data()
        counter = data.get("counter")
        quest_id = data.get("quest_id")
        answers_quantity = data.get("answers_quantity")
        await db_commands.add_text_answer(quest_id=quest_id, respondent_id=message.from_user.id,
                                          answer=message.text)
        if counter < answers_quantity:
            questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
            await message.answer(f"Вопрос №6: {questionnaire.questions[counter]}")
            counter += 1
            await state.update_data(counter=counter)

            await FillQE.A6.set()
        else:
            await FillQE.Approve.set()
            qe_text_answers = await db_commands.select_qe_text_answers(quest_id=quest_id,
                                                                       respondent_id=message.from_user.id)
            text = "Отлично, Вы заполнили анкету:\n"
            text += await parse_answers_text(qe_text_answers=qe_text_answers)
            await message.answer(text, reply_markup=text_answers_approve_kb)


async def get_6_answer_text(message: types.Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.finish()
        await message.answer("Прохождение опроса прекращено...\n"
                             "Главное меню:", reply_markup=main_menu_kb)
    else:
        data = await state.get_data()
        counter = data.get("counter")
        quest_id = data.get("quest_id")
        answers_quantity = data.get("answers_quantity")
        await db_commands.add_text_answer(quest_id=quest_id, respondent_id=message.from_user.id,
                                          answer=message.text)
        if counter < answers_quantity:
            questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
            await message.answer(f"Вопрос №7: {questionnaire.questions[counter]}")
            counter += 1
            await state.update_data(counter=counter)

            await FillQE.A7.set()
        else:
            await FillQE.Approve.set()
            qe_text_answers = await db_commands.select_qe_text_answers(quest_id=quest_id,
                                                                       respondent_id=message.from_user.id)
            text = "Отлично, Вы заполнили анкету:\n"
            text += await parse_answers_text(qe_text_answers=qe_text_answers)
            await message.answer(text, reply_markup=text_answers_approve_kb)


async def get_7_answer_text(message: types.Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.finish()
        await message.answer("Прохождение опроса прекращено...\n"
                             "Главное меню:", reply_markup=main_menu_kb)
    else:
        data = await state.get_data()
        counter = data.get("counter")
        quest_id = data.get("quest_id")
        answers_quantity = data.get("answers_quantity")
        await db_commands.add_text_answer(quest_id=quest_id, respondent_id=message.from_user.id,
                                          answer=message.text)
        if counter < answers_quantity:
            questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
            await message.answer(f"Вопрос №8: {questionnaire.questions[counter]}")
            counter += 1
            await state.update_data(counter=counter)

            await FillQE.A8.set()
        else:
            await FillQE.Approve.set()
            qe_text_answers = await db_commands.select_qe_text_answers(quest_id=quest_id,
                                                                       respondent_id=message.from_user.id)
            text = "Отлично, Вы заполнили анкету:\n"
            text += await parse_answers_text(qe_text_answers=qe_text_answers)
            await message.answer(text, reply_markup=text_answers_approve_kb)


async def get_8_answer_text(message: types.Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.finish()
        await message.answer("Прохождение опроса прекращено...\n"
                             "Главное меню:", reply_markup=main_menu_kb)
    else:
        data = await state.get_data()
        counter = data.get("counter")
        quest_id = data.get("quest_id")
        answers_quantity = data.get("answers_quantity")
        await db_commands.add_text_answer(quest_id=quest_id, respondent_id=message.from_user.id,
                                          answer=message.text)
        if counter < answers_quantity:
            questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
            await message.answer(f"Вопрос №9: {questionnaire.questions[counter]}")
            counter += 1
            await state.update_data(counter=counter)

            await FillQE.A9.set()
        else:
            await FillQE.Approve.set()
            qe_text_answers = await db_commands.select_qe_text_answers(quest_id=quest_id,
                                                                       respondent_id=message.from_user.id)
            text = "Отлично, Вы заполнили анкету:\n"
            text += await parse_answers_text(qe_text_answers=qe_text_answers)
            await message.answer(text, reply_markup=text_answers_approve_kb)


async def get_9_answer_text(message: types.Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.finish()
        await message.answer("Прохождение опроса прекращено...\n"
                             "Главное меню:", reply_markup=main_menu_kb)
    else:
        data = await state.get_data()
        counter = data.get("counter")
        quest_id = data.get("quest_id")
        answers_quantity = data.get("answers_quantity")
        await db_commands.add_text_answer(quest_id=quest_id, respondent_id=message.from_user.id,
                                          answer=message.text)
        if counter < answers_quantity:
            questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
            await message.answer(f"Вопрос №10: {questionnaire.questions[counter]}")
            counter += 1
            await state.update_data(counter=counter)

            await FillQE.A7.set()
        else:
            await FillQE.Approve.set()
            qe_text_answers = await db_commands.select_qe_text_answers(quest_id=quest_id,
                                                                       respondent_id=message.from_user.id)
            text = "Отлично, Вы заполнили анкету:\n"
            text += await parse_answers_text(qe_text_answers=qe_text_answers)
            await message.answer(text, reply_markup=text_answers_approve_kb)


async def get_10_answer_text(message: types.Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.finish()
        await message.answer("Прохождение опроса прекращено...\n"
                             "Главное меню:", reply_markup=main_menu_kb)
    else:
        data = await state.get_data()
        quest_id = data.get("quest_id")
        await db_commands.add_text_answer(quest_id=quest_id, respondent_id=message.from_user.id,
                                          answer=message.text)
        await FillQE.Approve.set()


async def approve_text_answers(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    approve = callback_data.get("answers_approve")
    data = await state.get_data()
    quest_id = data.get("quest_id")
    if approve == "true":
        await state.finish()
        await db_commands.set_complete_status(quest_id=quest_id, respondent_id=call.from_user.id, status="true")
        await call.message.answer("Отлично, Ваши ответы отправлены создателю опроса. Всё анонимно!",
                                  reply_markup=main_menu_kb)
    elif approve == "false":
        await db_commands.delete_qe_text_answers(quest_id=quest_id, respondent_id=call.from_user.id)
        await call.message.answer("Ваши ответы удалены",
                                  reply_markup=main_menu_kb)
        await state.finish()


def register_process_fill_text_questionnaire(dp: Dispatcher):
    dp.register_message_handler(get_1_answer_text, content_types=types.ContentType.TEXT, state=FillQE.A1)
    dp.register_message_handler(get_1_answer_text, content_types=types.ContentType.TEXT, state=FillQE.A2)
    dp.register_message_handler(get_1_answer_text, content_types=types.ContentType.TEXT, state=FillQE.A3)
    dp.register_message_handler(get_1_answer_text, content_types=types.ContentType.TEXT, state=FillQE.A4)
    dp.register_message_handler(get_1_answer_text, content_types=types.ContentType.TEXT, state=FillQE.A5)
    dp.register_message_handler(get_1_answer_text, content_types=types.ContentType.TEXT, state=FillQE.A6)
    dp.register_message_handler(get_1_answer_text, content_types=types.ContentType.TEXT, state=FillQE.A7)
    dp.register_message_handler(get_1_answer_text, content_types=types.ContentType.TEXT, state=FillQE.A8)
    dp.register_message_handler(get_1_answer_text, content_types=types.ContentType.TEXT, state=FillQE.A9)
    dp.register_message_handler(get_1_answer_text, content_types=types.ContentType.TEXT, state=FillQE.A10)
    dp.register_callback_query_handler(approve_text_answers, text_answers_approve_callback.filter(
        answers_approve=text_a_approves), state=FillQE.Approve)
