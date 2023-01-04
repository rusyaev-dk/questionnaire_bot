from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from tgbot.keyboards.default.qe_text_keyboards import main_menu_kb
from tgbot.keyboards.inline.qe_inline_keyboards import questionnaire_approve_kb, q_approve_callback, q_approves, \
    share_link_kb
from tgbot.misc.states import CreateTextQe
from tgbot.services.database import db_commands
from tgbot.services.service_functions import get_rand_id, parse_questions_text


async def get_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Укажите <b>количество</b> вопросов:")
    await CreateTextQe.Questions_qty.set()


async def create_questionnaire(message: types.Message, state: FSMContext):
    data = await state.get_data()
    title = data.get("title")
    while True:
        try:
            questions_quantity = int(message.text)
            if questions_quantity <= 0:
                await message.answer("Введите корректное значение.")
                return
            elif questions_quantity > 15:
                await message.answer("Опрос может состоять не более чем из 15 вопросов. Введите значение"
                                     " снова")
                return
            quest_id = get_rand_id(10)
            await state.update_data(quest_id=quest_id)
            await state.update_data(questions_quantity=questions_quantity)
            await state.update_data(counter=0)
            await db_commands.create_questionnaire(quest_id=quest_id, creator_id=message.from_user.id, title=title,
                                                   questions_quantity=questions_quantity, q_type="text")
            await message.answer("Введите 1-й вопрос:")
            await CreateTextQe.GetQuestion.set()
            break
        except ValueError:
            await message.answer("Введите целочисленное значение.")
            return


async def get_question_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    quest_id = data.get("quest_id")
    counter = data.get("counter")
    questions_quantity = data.get("questions_quantity")
    while True:
        await db_commands.add_question(quest_id=quest_id, question=message.text)
        counter += 1
        if counter < questions_quantity:
            await message.answer(f"Введите {counter + 1}-й вопрос:")
            await state.update_data(counter=counter)
            return

        else:
            questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
            text = await parse_questions_text(questionnaire=questionnaire)
            await message.answer(text, reply_markup=questionnaire_approve_kb)
            await CreateTextQe.Approve.set()
            break


async def approve_questionnaire(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    approve = callback_data.get("questions_approve")
    data = await state.get_data()
    quest_id = data.get("quest_id")
    if approve == "true":
        await state.finish()
        link = f"https://t.me/msu_talk_bot/?start={quest_id}"
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text="✅ Отлично, Ваш опрос добавлен в базу данных "
                                         "и доступен для прохождения другими пользователями.\n\n"
                                         f"📎 Ссылка для прохождения: <b>{link}</b>",
                                         reply_markup=share_link_kb(link))
        await call.message.answer("Главное меню:", reply_markup=main_menu_kb)
    elif approve == "false":
        await db_commands.delete_questionnaire(creator_id=call.from_user.id, quest_id=quest_id)
        await state.finish()
        await call.message.answer("❌ Создание опроса отменено. Главное меню:",
                                  reply_markup=main_menu_kb)


def register_create_text_qe(dp: Dispatcher):
    dp.register_message_handler(get_title, content_types=types.ContentType.TEXT, state=CreateTextQe.Title)
    dp.register_message_handler(create_questionnaire, content_types=types.ContentType.TEXT,
                                state=CreateTextQe.Questions_qty)

    dp.register_message_handler(get_question_text, content_types=types.ContentType.TEXT,
                                state=CreateTextQe.GetQuestion)

    dp.register_callback_query_handler(approve_questionnaire, q_approve_callback.filter(questions_approve=q_approves),
                                       state=CreateTextQe.Approve)
