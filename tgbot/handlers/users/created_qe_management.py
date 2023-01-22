import logging
import os

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from tgbot.keyboards.qe_reply_kbs import main_menu_kb
from tgbot.keyboards.qe_inline_kbs import created_qe_statistics_kb, qe_list_callback, \
    statistics_kb_callback, statistics_acts, file_type_kb, file_type_callback, f_types, delete_qe_approve_kb, \
    delete_qe_approve_callback, delete_qe_approves, qe_list_kb
from tgbot.misc.Excel.create_xlsx import create_xlsx_file
from tgbot.misc.states import CreatedQeStatistics

from tgbot.services.database import db_commands
from tgbot.misc.dependences import PASSED_BY_MINIMUM
from tgbot.services.service_functions import created_qe_info, statistics_qe_text


async def get_created_qe_statistics(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    qe_id = callback_data.get("qe_id")
    if qe_id == "main_menu":
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.message.answer("Главное меню:", reply_markup=main_menu_kb)
        await state.finish()
    else:
        questionnaire = await db_commands.select_questionnaire(qe_id=qe_id)
        qe_text = await created_qe_info(questionnaire=questionnaire)
        stat_text = await statistics_qe_text(questionnaire=questionnaire)

        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text=qe_text)
        keyboard = await created_qe_statistics_kb(is_active=questionnaire.is_active, qe_id=qe_id)
        await call.message.answer(text=stat_text, reply_markup=keyboard)
        await state.update_data(qe_id=qe_id)
        await CreatedQeStatistics.SelectStatsAct.set()


async def created_qe_management(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    act = callback_data.get("act")

    data = await state.get_data()
    qe_id = data.get("qe_id")
    questionnaire = await db_commands.select_questionnaire(qe_id=qe_id)

    if act == "get_file":
        passed_by = questionnaire.passed_by
        if passed_by >= PASSED_BY_MINIMUM:
            await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                             text="📎 Выберите <b>формат</b> файла:\n\n"
                                                  "ℹ️ Примечание: тут будет примечание.", reply_markup=file_type_kb)
            await CreatedQeStatistics.SelectFileType.set()
        else:
            await call.answer(f"👥 Чтобы получить файл с ответами, Ваш опрос должно пройти "
                              f"как минимум {PASSED_BY_MINIMUM} человек.", show_alert=True)

    elif act == "freeze_qe":
        await db_commands.freeze_questionnaire(qe_id=qe_id, is_active="false")
        await call.answer("Опрос остановлен.", show_alert=True)

        questionnaire = await db_commands.select_questionnaire(qe_id=qe_id)
        stat_text = await statistics_qe_text(questionnaire=questionnaire)
        keyboard = await created_qe_statistics_kb(is_active=questionnaire.is_active, qe_id=qe_id)
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=stat_text,
                                         reply_markup=keyboard)

    elif act == "resume_qe":
        await db_commands.freeze_questionnaire(qe_id=qe_id, is_active="true")
        await call.answer("Опрос возобновлён.", show_alert=True)

        questionnaire = await db_commands.select_questionnaire(qe_id=qe_id)
        stat_text = await statistics_qe_text(questionnaire=questionnaire)
        keyboard = await created_qe_statistics_kb(is_active=questionnaire.is_active, qe_id=qe_id)
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=stat_text,
                                         reply_markup=keyboard)

    elif act == "delete":
        await call.answer("⚠️ После удаления опроса пропадёт вся статистика и ответы. Восстановить опрос уже "
                          "не получится.", show_alert=True)
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text=f"Подтвердите удаление опроса: <b>{questionnaire.title}</b>",
                                         reply_markup=delete_qe_approve_kb)
        await CreatedQeStatistics.DeleteApprove.set()

    elif act == "step_back":
        keyboard = data.get("keyboard")
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text="🔍 Выберите опрос для отображения статистики:", reply_markup=keyboard)
        await CreatedQeStatistics.SelectQE.set()

    elif act == "main_menu":
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.message.answer("Главное меню:", reply_markup=main_menu_kb)
        await state.finish()


async def choose_file_type(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    f_type = callback_data.get("f_type")

    data = await state.get_data()
    qe_id = data.get("qe_id")

    questionnaire = await db_commands.select_questionnaire(qe_id=qe_id)
    stat_text = await statistics_qe_text(questionnaire=questionnaire)

    if f_type == "pdf":
        await call.answer("В разработке...")
        # await call.answer("⏳ Пожалуйста, подождите...", show_alert=True)
        # file_path = await create_pdf_file(questionnaire=questionnaire)
        # if file_path:
        #     await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        #     await call.message.answer_document(types.InputFile(rf"{file_path}"), caption="📌 Файл по Вашему опросу")
        #     keyboard = await created_qe_statistics_kb(is_active=questionnaire.is_active, qe_id=qe_id)
        #     await call.message.answer(text=stat_text, reply_markup=keyboard)
        #     os.remove(file_path)
        #     await CreatedQeStatistics.SelectStatsAct.set()
        # else:
        #     await call.answer("Что-то пошло не так...", show_alert=False)

    elif f_type == "xlsx":
        await call.answer("⏳ Пожалуйста, подождите...", show_alert=True)
        file_path = await create_xlsx_file(questionnaire=questionnaire)
        try:
            await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            await call.message.answer_document(types.InputFile(rf"{file_path}"), caption="📌 Файл по Вашему опросу")
            keyboard = await created_qe_statistics_kb(is_active=questionnaire.is_active, qe_id=qe_id)
            await call.message.answer(text=stat_text, reply_markup=keyboard)
            os.remove(file_path)
            await CreatedQeStatistics.SelectStatsAct.set()
        except Exception as e:
            logging.error(e)
            await call.answer("Что-то пошло не так. Сообщите об ошибке разработчику!", show_alert=True)
            await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            await call.message.answer("Главное меню:", reply_markup=main_menu_kb)
            await state.finish()

    elif f_type == "step_back":
        keyboard = await created_qe_statistics_kb(is_active=questionnaire.is_active, qe_id=qe_id)
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=stat_text,
                                         reply_markup=keyboard)
        await CreatedQeStatistics.SelectStatsAct.set()

    elif f_type == "main_menu":
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.message.answer(text="Главное меню:", reply_markup=main_menu_kb)
        await state.finish()


async def delete_qe_approve(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    approve = callback_data.get("approve")
    data = await state.get_data()
    qe_id = data.get("qe_id")

    if approve == "delete":
        await db_commands.delete_questionnaire(qe_id=qe_id)
        await call.answer("Опрос удалён.", show_alert=True)

        created_qes = await db_commands.select_user_created_qes(creator_id=call.from_user.id)
        if len(created_qes) > 0:
            keyboard = await qe_list_kb(questionnaires=created_qes)
            await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                             text="🔍 Выберите опрос для отображения статистики:", reply_markup=keyboard)
            await state.update_data(keyboard=keyboard)
            await CreatedQeStatistics.SelectQE.set()
        else:
            await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                             text="📭 У Вас нет созданных опросов.")
            await call.message.answer("Главное меню:", reply_markup=main_menu_kb)
            await state.finish()

    elif approve == "cancel":
        await call.answer("Удаление опроса отменено.", show_alert=False)
        questionnaire = await db_commands.select_questionnaire(qe_id=qe_id)
        stat_text = await statistics_qe_text(questionnaire=questionnaire)
        keyboard = await created_qe_statistics_kb(is_active=questionnaire.is_active, qe_id=qe_id)
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=stat_text,
                                         reply_markup=keyboard)
        await CreatedQeStatistics.SelectStatsAct.set()


def register_created_qe_management(dp: Dispatcher):
    dp.register_callback_query_handler(get_created_qe_statistics, qe_list_callback.filter(),
                                       state=CreatedQeStatistics.SelectQE)
    dp.register_callback_query_handler(created_qe_management, statistics_kb_callback.filter(act=statistics_acts),
                                       state=CreatedQeStatistics.SelectStatsAct)
    dp.register_callback_query_handler(choose_file_type, file_type_callback.filter(f_type=f_types),
                                       state=CreatedQeStatistics.SelectFileType)
    dp.register_callback_query_handler(delete_qe_approve, delete_qe_approve_callback.filter(approve=delete_qe_approves),
                                       state=CreatedQeStatistics.DeleteApprove)
