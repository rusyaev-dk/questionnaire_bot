from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove

from tgbot.keyboards.default.base_keyboards import main_menu_kb
from tgbot.keyboards.inline.questionnaire_keyboards import questionnaire_type_kb, q_type_callback, q_types
from tgbot.misc.states import CreateQE


async def create_questionnaire(message: types.Message, state: FSMContext):
    await message.answer("Вы запустили процесс создания опроса...",
                         reply_markup=ReplyKeyboardRemove())
    await message.answer("Каково типа будет Ваш опрос?",
                         reply_markup=questionnaire_type_kb)
    await state.set_state("q_type")
# СРОЧНО объединить тип кол-во и тайтл под общий стейт!!!


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


def register_process_main_menu(dp: Dispatcher):
    dp.register_message_handler(create_questionnaire, text="Создать опрос", state="*")
    dp.register_callback_query_handler(select_questionnaire_type, q_type_callback.filter(q_type=q_types),
                                       state="q_type")
