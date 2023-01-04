from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove

from tgbot.keyboards.default.qe_text_keyboards import main_menu_kb
from tgbot.keyboards.inline.qe_inline_keyboards import questionnaire_type_kb, q_type_callback, q_types, \
    qe_list_kb
from tgbot.misc.states import CreateTextQe, CreatedQeStatistics, PassedQeStatistics
from tgbot.services.database import db_commands


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
        keyboard = await qe_list_kb(created_questionnaires)
        await state.update_data(keyboard=keyboard)
        await message.answer("🔍 Выберите опрос для отображения статистики:",
                             reply_markup=keyboard)
    else:
        await message.answer("У Вас нет созданных опросов.")


async def get_user_passed_questionnaires(message: types.Message, state: FSMContext):
    user = await db_commands.select_user(id=message.from_user.id)
    passed_questionnaires = list(user.passed_questionnaires)
    if len(passed_questionnaires) > 0:
        await message.answer("Тут будет гайд.", reply_markup=ReplyKeyboardRemove())
        await PassedQeStatistics.SelectQE.set()
        keyboard = await qe_list_kb(passed_questionnaires)
        await state.update_data(keyboard=keyboard)
        await message.answer("Выберите опрос для отображения статистики:",
                             reply_markup=keyboard)
    else:
        await message.answer("Вы ещё не проходили опросы.")


def register_main_menu(dp: Dispatcher):
    dp.register_message_handler(create_questionnaire, text="📝 Создать опрос", state="*")
    dp.register_callback_query_handler(select_questionnaire_type, q_type_callback.filter(q_type=q_types),
                                       state="q_type")
    dp.register_message_handler(get_user_created_questionnaires, text="🗂 Созданные опросы", state="*")
    dp.register_message_handler(get_user_passed_questionnaires, text="📌 Пройденные опросы", state="*")
