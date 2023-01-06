import os

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from tgbot.keyboards.default.qe_text_keyboards import main_menu_kb
from tgbot.keyboards.inline.qe_inline_keyboards import created_qe_statistics_kb, qe_list_callback, \
    statistics_kb_callback, statistics_acts, file_type_kb, file_type_callback, f_types, delete_approve_kb, \
    delete_approve_callback, delete_approves, qe_list_kb
from tgbot.misc.states import CreatedQeStatistics
from tgbot.services.Excel.create_xlsx import create_xlsx_file
from tgbot.services.PDF.create_pdf import create_pdf_file
from tgbot.services.database import db_commands
from tgbot.services.dependences import PASSED_BY_MINIMUM
from tgbot.services.service_functions import get_created_questionnaire_info


async def get_created_qe_statistics(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
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
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=text,
                                         reply_markup=created_qe_statistics_kb(is_active=questionnaire.is_active))


async def created_qe_management(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    act = callback_data.get("act")

    data = await state.get_data()
    quest_id = data.get("quest_id")
    text = data.get("text")
    questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
    if act == "get_file":
        passed_by = questionnaire.passed_by
        if passed_by > PASSED_BY_MINIMUM:
            await CreatedQeStatistics.SelectFileType.set()
            await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                             text="📎 Выберите <b>расширение</b> файла:\n\n"
                                                  "📍 Примечание: тут будет примечание.", reply_markup=file_type_kb)
        else:
            await call.answer(f"👥 Чтобы получить файл с ответами, Ваш опрос должно пройти "
                              f"как минимум {PASSED_BY_MINIMUM} человек.", show_alert=True)

    elif act == "freeze":
        await db_commands.freeze_questionnaire(quest_id=quest_id, is_active="false")
        await call.answer("Опрос остановлен", show_alert=True)
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=text,
                                         reply_markup=created_qe_statistics_kb(is_active=questionnaire.is_active))

    elif act == "resume":
        await db_commands.freeze_questionnaire(quest_id=quest_id, is_active="true")
        await call.answer("Опрос возобновлён", show_alert=True)
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=text,
                                         reply_markup=created_qe_statistics_kb(is_active=questionnaire.is_active))

    elif act == "delete":
        await CreatedQeStatistics.ApproveDelete.set()
        await call.answer("⚠️ После удаления опрос восстановить уже никак не получится, а также пропадёт вся статистика"
                          " по данному опросу", show_alert=True)
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text=f"Подтвердите удаление опроса: <b>{questionnaire.title}</b>",
                                         reply_markup=delete_approve_kb)

    elif act == "step_back":
        await CreatedQeStatistics.SelectQE.set()
        keyboard = data.get("keyboard")
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text="🔍 Выберите опрос для отображения статистики:", reply_markup=keyboard)

    elif act == "main_menu":
        await state.finish()
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.message.answer("Главное меню:", reply_markup=main_menu_kb)


async def choose_file_type(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    f_type = callback_data.get("f_type")

    data = await state.get_data()
    quest_id = data.get("quest_id")
    text = data.get("text")
    questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
    qe_text_answers_tab = await db_commands.select_text_answers_tab(quest_id=quest_id)
    if f_type == "pdf":
        file_path = await create_pdf_file(quest_id=quest_id, qe_text_answers_tab=qe_text_answers_tab)
        if file_path:
            await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            await call.message.answer_document(types.InputFile(f"{file_path}"), caption="📌 Файл по Вашему опросу")
            await CreatedQeStatistics.SelectStatsAct.set()
            await call.message.answer(text=text,
                                      reply_markup=created_qe_statistics_kb(is_active=questionnaire.is_active))
            os.remove(file_path)
        else:
            await call.answer("Что-то пошло не так...", show_alert=False)

    elif f_type == "xlsx":
        file_path = await create_xlsx_file(quest_id=quest_id, qe_text_answers_tab=qe_text_answers_tab)
        if file_path:
            await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            await call.message.answer_document(types.InputFile(f"{file_path}"), caption="📌 Файл по Вашему опросу")
            await CreatedQeStatistics.SelectStatsAct.set()
            await call.message.answer(text=text,
                                      reply_markup=created_qe_statistics_kb(is_active=questionnaire.is_active))
            os.remove(file_path)
        else:
            await call.answer("Что-то пошло не так. Сообщите об ошибке разработчику!", show_alert=True)

    elif f_type == "step_back":
        await CreatedQeStatistics.SelectStatsAct.set()
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=text,
                                         reply_markup=created_qe_statistics_kb(is_active=questionnaire.is_active))

    elif f_type == "main_menu":
        await state.finish()
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.message.answer(text="Главное меню:", reply_markup=main_menu_kb)


async def delete_qe_approve(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    approve = callback_data.get("approve")
    data = await state.get_data()
    quest_id = data.get("quest_id")

    questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
    if approve == "delete":
        await db_commands.delete_questionnaire(quest_id=quest_id)
        await db_commands.remove_user_created_qe(creator_id=call.from_user.id, quest_id=quest_id)
        await call.answer("Опрос удалён", show_alert=True)

        user = await db_commands.select_user(id=call.from_user.id)
        created_questionnaires = user.created_questionnaires
        keyboard = await qe_list_kb(created_questionnaires)
        if len(created_questionnaires) > 0:
            await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                             text="🔍 Выберите опрос для отображения статистики:", reply_markup=keyboard)
            await state.update_data(keyboard=keyboard)
            await CreatedQeStatistics.SelectQE.set()
        else:
            await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                             text="У вас нет созданных опросов.")
            await state.finish()
            await call.message.answer("Главное меню:", reply_markup=main_menu_kb)

    elif approve == "cancel":
        await call.answer("Удаление опроса отменено", show_alert=False)
        await CreatedQeStatistics.SelectStatsAct.set()
        text = data.get("text")
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=text,
                                         reply_markup=created_qe_statistics_kb(is_active=questionnaire.is_active))


def register_created_qe_management(dp: Dispatcher):
    dp.register_callback_query_handler(get_created_qe_statistics, qe_list_callback.filter(),
                                       state=CreatedQeStatistics.SelectQE)
    dp.register_callback_query_handler(created_qe_management, statistics_kb_callback.filter(act=statistics_acts),
                                       state=CreatedQeStatistics.SelectStatsAct)
    dp.register_callback_query_handler(choose_file_type, file_type_callback.filter(f_type=f_types),
                                       state=CreatedQeStatistics.SelectFileType)
    dp.register_callback_query_handler(delete_qe_approve, delete_approve_callback.filter(approve=delete_approves),
                                       state=CreatedQeStatistics.ApproveDelete)
