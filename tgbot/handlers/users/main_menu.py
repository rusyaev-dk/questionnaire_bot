from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove

from tgbot.keyboards.qe_inline_kbs import qe_list_kb
from tgbot.misc.dependences import CREATED_GUIDE_MESSAGE, BOT_INFO_MESSAGE, PASSED_GUIDE_MESSAGE
from tgbot.misc.states import CreatedQeStatistics, PassedQeStatistics, CreateQe
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
async def user_statistics(message: types.Message):
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

    await message.answer("📊 Ваша статистика:\n"
                         f"• Создано опросов: <b>{user.created_qe_quantity}</b>\n"
                         f"• Пройдено опросов: <b>{user.passed_qe_quantity}</b>\n"
                         f"• Всего опрошено: <b>{total_respondents}</b> чел.\n"
                         f"• По Вашим ссылкам перешло: <b>{user.link_clicks}</b> чел.\n"
                         f"• Процент прохождения Ваших опросов: <b>{average_pass_percent:.1f}%</b>")


@rate_limit(limit=2, key=2)
async def developer_info(message: types.Message):
    await message.answer(text=BOT_INFO_MESSAGE)


def register_main_menu(dp: Dispatcher):
    dp.register_message_handler(create_questionnaire, text="📝 Создать опрос", state="*")
    dp.register_message_handler(user_created_questionnaires, text="🗂 Созданные опросы", state="*")
    dp.register_message_handler(user_passed_questionnaires, text="🗃 Пройденные опросы", state="*")
    dp.register_message_handler(user_statistics, text="📊 Моя статистика", state="*")
    dp.register_message_handler(developer_info, text="🤖 О боте", state="*")
