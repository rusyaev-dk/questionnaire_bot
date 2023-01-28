from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from tgbot.keyboards.qe_reply_kbs import main_menu_kb
from tgbot.keyboards.qe_inline_kbs import passed_qe_statistics_kb, qe_list_callback, \
    statistics_kb_callback, statistics_acts
from tgbot.misc.states import PassedQeStatistics
from tgbot.services.database import db_commands
from tgbot.services.service_functions import passed_qe_info


async def get_passed_qe_statistics(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    qe_id = callback_data.get("qe_id")
    if qe_id == "main_menu":
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.message.answer("Главное меню:", reply_markup=main_menu_kb)
        await state.reset_data()
        await state.finish()
    else:
        questionnaire = await db_commands.select_questionnaire(qe_id=qe_id)
        message_text = await passed_qe_info(respondent_id=call.from_user.id, questionnaire=questionnaire,
                                            markdown=False)
        share_text = await passed_qe_info(respondent_id=call.from_user.id, questionnaire=questionnaire,
                                          markdown=True)
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text=message_text, reply_markup=passed_qe_statistics_kb(share_text=share_text))
        await PassedQeStatistics.SelectStatsAct.set()


async def passed_qe_management(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    act = callback_data.get("act")
    if act == "step_back":
        data = await state.get_data()
        keyboard = data.get("keyboard")
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text="🔍 Выберите опрос для отображения информации:",
                                         reply_markup=keyboard)
        await PassedQeStatistics.SelectQE.set()

    elif act == "main_menu":
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.message.answer("Главное меню:", reply_markup=main_menu_kb)
        await state.reset_data()
        await state.finish()


def register_passed_qe_management(dp: Dispatcher):
    dp.register_callback_query_handler(get_passed_qe_statistics, qe_list_callback.filter(),
                                       state=PassedQeStatistics.SelectQE)
    dp.register_callback_query_handler(passed_qe_management, statistics_kb_callback.filter(act=statistics_acts),
                                       state=PassedQeStatistics.SelectStatsAct)
