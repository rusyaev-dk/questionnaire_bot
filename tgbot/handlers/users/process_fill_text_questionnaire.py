from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from tgbot.misc.states import FillQE
from tgbot.services.database import db_commands


async def get_1_answer_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    quest_id = data.get("quest_id")
    questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
    await db_commands.create_qe_text_answers(quest_id=quest_id, respondent_id=message.from_user.id,
                                                               answers_quantity=questionnaire.questions_quantity)
    await db_commands.add_text_answer(quest_id=quest_id, respondent_id=message.from_user.id,
                                      answer=message.text)
    qe_text_answers = await db_commands.select_qe_text_answers(quest_id=quest_id, respondent_id=message.from_user.id)
    await message.answer(f"{qe_text_answers.answers[0]}")
    await state.finish()


def register_process_fill_text_questionnaire(dp: Dispatcher):
    dp.register_message_handler(get_1_answer_text, content_types=types.ContentType.TEXT, state=FillQE.A1)

