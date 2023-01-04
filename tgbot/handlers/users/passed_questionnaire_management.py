from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from tgbot.keyboards.default.qe_text_keyboards import main_menu_kb
from tgbot.keyboards.inline.qe_inline_keyboards import passed_qe_statistics_kb, qe_list_callback, \
    statistics_kb_callback, statistics_acts
from tgbot.misc.states import PassedQeStatistics
from tgbot.services.service_functions import get_passed_questionnaire_info


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


def register_passed_qe_management(dp: Dispatcher):
    dp.register_callback_query_handler(get_passed_qe_statistics, qe_list_callback.filter(),
                                       state=PassedQeStatistics.SelectQE)
    dp.register_callback_query_handler(passed_qe_management, statistics_kb_callback.filter(act=statistics_acts),
                                       state=PassedQeStatistics.SelectStatsAct)
