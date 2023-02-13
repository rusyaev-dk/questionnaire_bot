from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove

from tgbot.keyboards.qe_inline_kbs import qe_list_kb, user_profile_menu_kb, user_profile_menu_callback, \
    user_profile_options
from tgbot.keyboards.qe_reply_kbs import main_menu_kb
from tgbot.misc.dependences import CREATED_GUIDE_MESSAGE, PASSED_GUIDE_MESSAGE
from tgbot.misc.states import CreatedQeStatistics, PassedQeStatistics, CreateQe, UserProfileMenu
from tgbot.misc.throttling_function import rate_limit
from tgbot.services.database import db_commands


@rate_limit(3)
async def create_questionnaire(message: types.Message):
    await message.answer("🏷 Введите <b>название</b> опроса:", reply_markup=ReplyKeyboardRemove())
    await CreateQe.Title.set()


@rate_limit(2)
async def user_created_questionnaires(message: types.Message, state: FSMContext):
    created_qes = await db_commands.select_user_created_qes(creator_id=message.from_user.id)
    if len(created_qes) > 0:
        await message.answer(text=CREATED_GUIDE_MESSAGE, reply_markup=ReplyKeyboardRemove())
        keyboard = await qe_list_kb(questionnaires=created_qes)
        await state.update_data(keyboard=keyboard)
        await message.answer("🔍 Выберите опрос для отображения статистики:",
                             reply_markup=keyboard)
        await CreatedQeStatistics.SelectQE.set()
    else:
        await message.answer("📂 У Вас нет созданных опросов.")


@rate_limit(2)
async def user_passed_questionnaires(message: types.Message, state: FSMContext):
    passed_qes = await db_commands.select_user_passed_qes(respondent_id=message.from_user.id)
    if len(passed_qes) > 0:
        await message.answer(text=PASSED_GUIDE_MESSAGE, reply_markup=ReplyKeyboardRemove())
        keyboard = await qe_list_kb(questionnaires=passed_qes)
        await state.update_data(keyboard=keyboard)
        await message.answer("🔍 Выберите опрос для отображения информации:",
                             reply_markup=keyboard)
        await PassedQeStatistics.SelectQE.set()
    else:
        user = await db_commands.select_user(id=message.from_user.id)
        passed_qe_quantity = user.passed_qe_quantity
        if passed_qe_quantity:
            await message.answer("🚮 Опросы, которые Вы проходили, были удалены авторами.")
        else:
            await message.answer("📭 Вы ещё не проходили опросы.")


@rate_limit(2)
async def user_profile(message: types.Message):
    await message.answer("📍 В этом разделе предоставляется статистика профиля и возможность изменить "
                         "контактные данные", reply_markup=ReplyKeyboardRemove())

    await UserProfileMenu.SelectOption.set()

    user = await db_commands.select_user(id=message.from_user.id)
    created_qes = await db_commands.select_user_created_qes(creator_id=message.from_user.id)

    total_respondents = 0
    pass_percent = 0
    for created_qe in created_qes:
        qe_id = created_qe.qe_id
        questionnaire = await db_commands.select_questionnaire(qe_id=qe_id)
        if questionnaire.started_by > 0:
            pass_percent += questionnaire.passed_by / questionnaire.started_by * 100
        total_respondents += questionnaire.passed_by

    if len(created_qes) > 0:
        average_pass_percent = pass_percent / len(created_qes)
    else:
        average_pass_percent = 0

    info = user.email
    if info is None:
        info = "отсутствует"

    await message.answer("🔖 Ваш профиль:\n"
                         f"• Контактная информация: <b>{info}</b>\n"
                         "\n📊 Ваша статистика:\n"
                         f"• Создано опросов: <b>{user.created_qe_quantity}</b>\n"
                         f"• Пройдено опросов: <b>{user.passed_qe_quantity}</b>\n"
                         f"• Всего опрошено: <b>{total_respondents}</b> чел.\n"
                         f"• По Вашим ссылкам перешло: <b>{user.link_clicks}</b> чел.\n"
                         f"• Процент прохождения Ваших опросов: <b>{average_pass_percent:.1f}%</b>",
                         reply_markup=user_profile_menu_kb)


@rate_limit(1)
async def select_user_profile_option(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    option = callback_data.get("option")
    if option == "change_email":
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.message.answer("📩 Введите новый адрес электронной почты:", reply_markup=ReplyKeyboardRemove())
        await UserProfileMenu.UpdateEmail.set()
    elif option == "main_menu":
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.message.answer("Главное меню:", reply_markup=main_menu_kb)
        await state.reset_data()
        await state.finish()


@rate_limit(1)
async def update_user_email(message: types.Message, state: FSMContext):
    if "@" not in message.text or "." not in message.text:
        await message.answer("❗️ Введите корректный адрес электронной почты.")
        return
    await db_commands.update_user_email(user_id=message.from_user.id, email=message.text)
    await message.answer("✅ Ваши контактные данные изменены. Главное меню:", reply_markup=main_menu_kb)
    await state.reset_data()
    await state.finish()


def register_main_menu(dp: Dispatcher):
    dp.register_message_handler(create_questionnaire, text="📝 Создать опрос", state="*")
    dp.register_message_handler(user_created_questionnaires, text="🗂 Созданные опросы", state="*")
    dp.register_message_handler(user_passed_questionnaires, text="🗃 Пройденные опросы", state="*")
    dp.register_message_handler(user_profile, text="🔖 Мой профиль", state="*")

    dp.register_callback_query_handler(select_user_profile_option,
                                       user_profile_menu_callback.filter(option=user_profile_options),
                                       state=UserProfileMenu.SelectOption)
    dp.register_message_handler(update_user_email, content_types=types.ContentType.TEXT,
                                state=UserProfileMenu.UpdateEmail)
