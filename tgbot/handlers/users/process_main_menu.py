from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove

from tgbot.keyboards.default.base_keyboards import main_menu_kb
from tgbot.keyboards.inline.questionnaire_keyboards import questionnaire_type_kb, q_type_callback, q_types
from tgbot.misc.states import CreateQE
from tgbot.services.database import db_commands
from tgbot.services.service_functions import get_questionnaire_info


async def create_questionnaire(message: types.Message, state: FSMContext):
    await message.answer("Вы запустили процесс создания опроса...",
                         reply_markup=ReplyKeyboardRemove())
    await message.answer("Каково типа будет Ваш опрос?",
                         reply_markup=questionnaire_type_kb)
    await state.set_state("q_type")


async def select_questionnaire_type(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    q_type = callback_data.get("q_type")
    if q_type == "test":
        await call.answer("В разработке...", show_alert=False)
        # await state.finish()
    elif q_type == "text":
        await state.finish()
        await call.message.answer("Отлично, укажите название Вашего опроса:")
        await CreateQE.Title.set()
    else:
        await state.finish()
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text="Создание опроса отменено")
        await call.message.answer("Главное меню:", reply_markup=main_menu_kb)


async def get_user_questionnaires(message: types.Message):
    user = await db_commands.select_user(id=message.from_user.id)
    user_questionnaires = list(user.user_questionnaires)
    if len(user_questionnaires) > 0:
        text = "Список Ваших действующих опросов:\n"
        for i in range(0, len(user_questionnaires)):
            questionnaire = await db_commands.select_questionnaire(quest_id=user_questionnaires[i])
            info = await get_questionnaire_info(questionnaire)
            text += (f"Опрос №{i+1}:" + f"\n{info}")
        await message.answer(f"{text}")
    else:
        await message.answer("Пока что у Вас нет опросов...")


def register_process_main_menu(dp: Dispatcher):
    dp.register_message_handler(get_user_questionnaires, text="Мои опросы", state="*")
    dp.register_message_handler(create_questionnaire, text="Создать опрос", state="*")
    dp.register_callback_query_handler(select_questionnaire_type, q_type_callback.filter(q_type=q_types),
                                       state="q_type")

