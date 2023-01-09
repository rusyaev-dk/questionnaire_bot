import re
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart

from tgbot.keyboards.default.qe_text_keyboards import main_menu_kb, cancel_fill_qe
from tgbot.keyboards.inline.qe_inline_keyboards import replay_qe_approve_kb, replay_qe_approve_callback, \
    replay_approves, generate_answer_options
from tgbot.misc.states import FillQe
from tgbot.misc.throttling_function import rate_limit
from tgbot.services.database import db_commands
from tgbot.services.database.db_commands import increase_qe_started_by
from tgbot.services.service_functions import parse_answer_options


@rate_limit(3)
async def bot_start(message: types.Message):
    await message.answer("🤖 Привет! Это <b>тестовый</b> бот для создания опросов и прохождения их другими людьми. "
                         "Пока что бот находится на ранней стадии своего развития, так что могут возникать ошибки!",
                         reply_markup=main_menu_kb)
    await db_commands.add_user(id=message.from_user.id, name=message.from_user.full_name)


@rate_limit(3)
async def deeplink_bot_start(message: types.Message, state: FSMContext):
    args = message.get_args()
    await db_commands.add_user(id=message.from_user.id, name=message.from_user.full_name)
    if len(args) == 10:
        questionnaire = await db_commands.select_questionnaire(quest_id=args)
        if questionnaire:
            user = await db_commands.select_user(id=message.from_user.id)
            user_passed_qe = user.passed_questionnaires
            if args in user_passed_qe:
                await message.answer(f"❗️ Вы уже прошли опрос <b>{questionnaire.title}</b>. Хотите пройти его "
                                     "заново? В этом случае Ваши предыдущие ответы будут удалены.",
                                     reply_markup=replay_qe_approve_kb)
                await state.set_state("replay_approve")
                await state.update_data(quest_id=args)
            else:
                if questionnaire.is_active == "true":
                    await increase_qe_started_by(quest_id=questionnaire.quest_id)
                    questions = questionnaire.questions

                    if questions[0][0] == "closed":
                        answers_list = questionnaire.answer_options  # two-dimensional list
                        answer_options = answers_list[0]
                        text = await parse_answer_options(answer_options=answer_options)
                        await message.answer(f"❓ 1-й вопрос: {questionnaire.questions[0][1]}\n\n{text}",
                                             reply_markup=generate_answer_options(answers_quantity=len(answer_options)))
                        await state.update_data(closed_counter=1)
                        await FillQe.ClosedAnswer.set()
                    else:
                        await message.answer(f"🔍 Вы начали прохождение опроса: {questionnaire.title}\n"
                                             f"❓ 1-й вопрос: {questionnaire.questions[0][1]}")
                        await state.update_data(closed_counter=0)
                        await FillQe.OpenAnswer.set()

                    await state.update_data(quest_id=questionnaire.quest_id, counter=0,
                                            answers_quantity=questionnaire.questions_quantity)
                    await db_commands.create_qe_answers(respondent_id=message.from_user.id,
                                                        quest_id=questionnaire.quest_id, title=questionnaire.title,
                                                        answers_quantity=questionnaire.questions_quantity)

                else:
                    await message.answer("⛔️ Данный опрос был остановлен автором.", reply_markup=main_menu_kb)
        else:
            await message.answer("🚫 Опрос не найден.", reply_markup=main_menu_kb)
    else:
        await message.answer("❗️ Ссылка, по которой Вы перешли, недействительна.", reply_markup=main_menu_kb)


async def replay_qe_approve(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    approve = callback_data.get("approve")
    if approve == "cancel":
        await state.finish()
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text="❌ Прохождение опроса отменено")
        await call.message.answer("Главное меню:", reply_markup=main_menu_kb)
    else:
        data = await state.get_data()
        quest_id = data.get("quest_id")
        questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
        if questionnaire:
            if questionnaire.is_active == "true":
                await increase_qe_started_by(quest_id=questionnaire.quest_id)
                questions = questionnaire.questions

                if questions[0][0] == "closed":
                    answers_list = questionnaire.answer_options  # two-dimensional list
                    answer_options = answers_list[0]
                    text = await parse_answer_options(answer_options=answer_options)
                    await call.message.answer(f"❓ 1-й вопрос: {questionnaire.questions[0][1]}\n\n{text}",
                                              reply_markup=generate_answer_options(answers_quantity=len(answer_options)))
                    await state.update_data(closed_counter=1)
                    await FillQe.ClosedAnswer.set()
                else:
                    await call.message.answer(f"🔍 Вы начали прохождение опроса: {questionnaire.title}\n"
                                              f"❓ 1-й вопрос: {questionnaire.questions[0][1]}")
                    await state.update_data(closed_counter=0)
                    await FillQe.OpenAnswer.set()

                await state.update_data(quest_id=questionnaire.quest_id, counter=0,
                                        answers_quantity=questionnaire.questions_quantity)
                await db_commands.create_qe_answers(respondent_id=call.from_user.id,
                                                    quest_id=questionnaire.quest_id, title=questionnaire.title,
                                                    answers_quantity=questionnaire.questions_quantity)
            else:
                await call.message.answer("⛔️ Данный опрос был остановлен автором.", reply_markup=main_menu_kb)
        else:
            await call.message.answer("🚫 Опрос не найден.", reply_markup=main_menu_kb)


def register_bot_start(dp: Dispatcher):
    dp.register_message_handler(deeplink_bot_start, CommandStart(deep_link=re.compile(r"^[a-zA-Z0-9]{1,10}$")),
                                state="*")
    dp.register_callback_query_handler(replay_qe_approve, replay_qe_approve_callback.filter(approve=replay_approves),
                                       state="replay_approve")
    dp.register_message_handler(bot_start, CommandStart(), state="*")
