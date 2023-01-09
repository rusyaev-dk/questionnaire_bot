from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove

from tgbot.keyboards.inline.qe_inline_keyboards import qe_list_kb
from tgbot.misc.states import CreatedQeStatistics, PassedQeStatistics, CreateQe
from tgbot.services.database import db_commands


async def create_questionnaire(message: types.Message):
    await message.answer("✏️ Введите <b>название</b> опроса:", reply_markup=ReplyKeyboardRemove())
    await CreateQe.Title.set()


async def get_user_created_questionnaires(message: types.Message, state: FSMContext):
    user = await db_commands.select_user(id=message.from_user.id)
    created_questionnaires = user.created_questionnaires
    if len(created_questionnaires) > 0:
        await message.answer("Тут будет гайд.", reply_markup=ReplyKeyboardRemove())
        await CreatedQeStatistics.SelectQE.set()
        keyboard = await qe_list_kb(created_questionnaires)
        await state.update_data(keyboard=keyboard)
        await message.answer("🔍 Выберите опрос для отображения статистики:",
                             reply_markup=keyboard)
    else:
        await message.answer("📭 У Вас нет созданных опросов.")


async def get_user_passed_questionnaires(message: types.Message, state: FSMContext):
    user = await db_commands.select_user(id=message.from_user.id)
    passed_questionnaires = user.passed_questionnaires
    if len(passed_questionnaires) > 0:
        await message.answer("Тут будет гайд.", reply_markup=ReplyKeyboardRemove())
        await PassedQeStatistics.SelectQE.set()
        keyboard = await qe_list_kb(passed_questionnaires)
        await state.update_data(keyboard=keyboard)
        await message.answer("🔍 Выберите опрос для отображения статистики:",
                             reply_markup=keyboard)
    else:
        await message.answer("📭 Вы ещё не проходили опросы.")


def register_main_menu(dp: Dispatcher):
    dp.register_message_handler(create_questionnaire, text="📝 Создать опрос", state="*")
    dp.register_message_handler(get_user_created_questionnaires, text="🗂 Созданные опросы", state="*")
    dp.register_message_handler(get_user_passed_questionnaires, text="📌 Пройденные опросы", state="*")
