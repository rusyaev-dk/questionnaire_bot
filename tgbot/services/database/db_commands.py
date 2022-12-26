from typing import List

from asyncpg import UniqueViolationError
from sqlalchemy import and_

from tgbot.services.database.db_gino import db
from tgbot.services.database.db_models import User, Questionnaire, QuestionnaireTextAnswers


async def add_user(id: int, name: str):
    try:
        user = User(id=id, name=name)
        await user.create()
    except UniqueViolationError:
        print("Пользователь уже есть в базе данных!")
        pass


async def select_user(id: int):
    user = await User.query.where(User.id == id).gino.first()
    return user


async def select_all_users():
    users = await User.query.gino.all()
    return users


async def count_users():
    total = await db.func.count(User.id).gino.scalar()
    return total


async def create_questionnaire(quest_id: str, creator_id: int, title: str, questions_quantity: int):
    try:
        questionnaire = Questionnaire(quest_id=quest_id, creator_id=creator_id, title=title,
                                      questions_quantity=questions_quantity)
        await questionnaire.create()

        user = await select_user(creator_id)
        quest_id_arr = list(user.user_questionnaires)
        quest_id_arr.append(quest_id)
        await user.update(user_questionnaires=quest_id_arr).apply()
    except UniqueViolationError:
        print("Опрос уже существует")
        pass


async def select_questionnaire(quest_id: str):
    questionnaire = await Questionnaire.query.where(Questionnaire.quest_id == quest_id).gino.first()
    return questionnaire


async def delete_questionnaire(creator_id: int, quest_id: str):
    questionnaire = await Questionnaire.query.where(Questionnaire.quest_id == quest_id).gino.first()

    user = await select_user(creator_id)
    quest_id_arr = list(user.user_questionnaires)
    quest_id_arr.remove(f"{quest_id}")
    await user.update(user_questionnaires=quest_id_arr).apply()
    await questionnaire.delete()
    return


async def add_question(quest_id: str, question: str):
    questionnaire = await Questionnaire.query.where(Questionnaire.quest_id == quest_id).gino.first()
    questions_arr = list(questionnaire.questions)
    questions_arr.append(question)
    await questionnaire.update(questions=questions_arr).apply()


async def create_qe_text_answers(quest_id: str, respondent_id: int, answers_quantity: int):
    try:
        qe_text_answers = QuestionnaireTextAnswers(quest_id=quest_id, respondent_id=respondent_id,
                                                   answers_quantity=answers_quantity)
        await qe_text_answers.create()
    except Exception as e:
        print(e)
        pass


async def select_qe_text_answers(quest_id: str, respondent_id: int):
    qe_text_answers = await QuestionnaireTextAnswers.query.where(and_(
        QuestionnaireTextAnswers.quest_id == quest_id,
        QuestionnaireTextAnswers.respondent_id == respondent_id)).gino.first()
    return qe_text_answers


async def add_text_answer(quest_id: str, respondent_id: int, answer: str):
    qe_text_answers = await QuestionnaireTextAnswers.query.where(and_(
        QuestionnaireTextAnswers.quest_id == quest_id,
        QuestionnaireTextAnswers.respondent_id == respondent_id)).gino.first()
    answers_arr = list(qe_text_answers.answers)
    answers_arr.append(answer)
    await qe_text_answers.update(answers=answers_arr).apply()
