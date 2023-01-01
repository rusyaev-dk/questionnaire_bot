from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove

from tgbot.keyboards.default.base_keyboards import main_menu_kb
from tgbot.keyboards.inline.questionnaire_keyboards import questionnaire_type_kb, q_type_callback, q_types, \
    generate_qe_list, created_qe_statistics_kb, qe_list_callback, statistics_kb_callback, statistics_acts, \
    passed_qe_statistics_kb
from tgbot.misc.states import CreateTextQe, CreatedQeStatistics, PassedQeStatistics
from tgbot.services.database import db_commands
from tgbot.services.service_functions import get_created_questionnaire_info, get_passed_questionnaire_info


async def create_questionnaire(message: types.Message, state: FSMContext):
    await message.answer("Тут будет гайд по созданию опроса.",
                         reply_markup=ReplyKeyboardRemove())
    await message.answer("🔍 Какого <b>типа</b> будет опрос?",
                         reply_markup=questionnaire_type_kb)
    await state.set_state("q_type")


async def select_questionnaire_type(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    q_type = callback_data.get("q_type")
    if q_type == "test":
        await call.answer("Эта опция в разработке :(", show_alert=False)
    elif q_type == "text":
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text="✏️ Отлично, укажите <b>название</b> опроса:")
        await CreateTextQe.Title.set()
    else:
        await state.finish()
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text="❌ Создание опроса отменено")
        await call.message.answer("Главное меню:", reply_markup=main_menu_kb)


async def get_user_created_questionnaires(message: types.Message, state: FSMContext):
    user = await db_commands.select_user(id=message.from_user.id)
    created_questionnaires = list(user.created_questionnaires)
    if len(created_questionnaires) > 0:
        await message.answer("Тут будет гайд.", reply_markup=ReplyKeyboardRemove())
        await CreatedQeStatistics.SelectQE.set()
        keyboard = await generate_qe_list(created_questionnaires)
        await state.update_data(keyboard=keyboard)
        await message.answer("Выберите опрос для отображения статистики:",
                             reply_markup=keyboard)
    else:
        await message.answer("Вы ещё не создавали опросы...")


async def get_questionnaire_statistics(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    quest_id = callback_data.get("quest_id")
    if quest_id == "main_menu":
        await state.finish()
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.message.answer("Главное меню:", reply_markup=main_menu_kb)
    else:
        await CreatedQeStatistics.SelectStatsAct.set()
        await state.update_data(quest_id=quest_id)
        questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
        text = await get_created_questionnaire_info(questionnaire)
        await state.update_data(text=text)
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text=text, reply_markup=created_qe_statistics_kb(is_active=questionnaire.is_active))


async def created_qe_management(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    act = callback_data.get("act")
    data = await state.get_data()
    if act == "get_file":
        await call.answer("Эта опция в разработке :(", show_alert=False)

    elif act == "answers":
        await call.answer("Эта опция в разработке :(", show_alert=False)

    elif act == "freeze":
        quest_id = data.get("quest_id")
        text = data.get("text")
        await db_commands.freeze_questionnaire(quest_id=quest_id, is_active="false")
        await call.answer("Опрос остановлен", show_alert=True)
        questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text=text, reply_markup=created_qe_statistics_kb(is_active=questionnaire.is_active))
    elif act == "resume":
        quest_id = data.get("quest_id")
        text = data.get("text")
        await db_commands.freeze_questionnaire(quest_id=quest_id, is_active="true")
        await call.answer("Опрос возобновлён", show_alert=True)
        questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text=text, reply_markup=created_qe_statistics_kb(is_active=questionnaire.is_active))

    elif act == "step_back":
        await CreatedQeStatistics.SelectQE.set()
        keyboard = data.get("keyboard")
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text="Выберите опрос для отображения статистики:",
                                         reply_markup=keyboard)
    elif act == "main_menu":
        await state.finish()
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.message.answer("Главное меню:", reply_markup=main_menu_kb)


async def get_user_passed_questionnaires(message: types.Message, state: FSMContext):
    user = await db_commands.select_user(id=message.from_user.id)
    passed_questionnaires = list(user.passed_questionnaires)
    if len(passed_questionnaires) > 0:
        await message.answer("Тут будет гайд.", reply_markup=ReplyKeyboardRemove())
        await PassedQeStatistics.SelectQE.set()
        keyboard = await generate_qe_list(passed_questionnaires)
        await state.update_data(keyboard=keyboard)
        await message.answer("Выберите опрос для отображения статистики:",
                             reply_markup=keyboard)
    else:
        await message.answer("Вы ещё не проходили опросы.")


async def get_passed_qe_statistics(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    quest_id = callback_data.get("quest_id")
    if quest_id == "main_menu":
        await state.finish()
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.message.answer("Главное меню:", reply_markup=main_menu_kb)
    else:
        await PassedQeStatistics.SelectStatsAct.set()
        message_text = await get_passed_questionnaire_info(respondent_id=call.from_user.id,
                                                           quest_id=quest_id, markdown=False)
        share_text = await get_passed_questionnaire_info(respondent_id=call.from_user.id,
                                                         quest_id=quest_id, markdown=True)
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text=message_text, reply_markup=passed_qe_statistics_kb(share_text=share_text))


async def passed_qe_management(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    act = callback_data.get("act")
    if act == "step_back":
        data = await state.get_data()
        keyboard = data.get("keyboard")
        await PassedQeStatistics.SelectQE.set()
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text="Выберите опрос для отображения статистики:",
                                         reply_markup=keyboard)

    elif act == "main_menu":
        await state.finish()
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.message.answer("Главное меню:", reply_markup=main_menu_kb)


def register_process_main_menu(dp: Dispatcher):
    dp.register_message_handler(create_questionnaire, text="📝 Создать опрос", state="*")
    dp.register_callback_query_handler(select_questionnaire_type, q_type_callback.filter(q_type=q_types),
                                       state="q_type")

    dp.register_message_handler(get_user_created_questionnaires, text="🗂 Созданные опросы", state="*")
    dp.register_callback_query_handler(get_questionnaire_statistics, qe_list_callback.filter(),
                                       state=CreatedQeStatistics.SelectQE)
    dp.register_callback_query_handler(created_qe_management, statistics_kb_callback.filter(act=statistics_acts),
                                       state=CreatedQeStatistics.SelectStatsAct)

    dp.register_message_handler(get_user_passed_questionnaires, text="📌 Пройденные опросы", state="*")
    dp.register_callback_query_handler(get_passed_qe_statistics, qe_list_callback.filter(),
                                       state=PassedQeStatistics.SelectQE)
    dp.register_callback_query_handler(passed_qe_management, statistics_kb_callback.filter(act=statistics_acts),
                                       state=PassedQeStatistics.SelectStatsAct)
