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


async def create_questionnaire(quest_id: str, creator_id: int, title: str, q_type: str, questions_quantity: int):
    try:
        questionnaire = Questionnaire(quest_id=quest_id, creator_id=creator_id, title=title,
                                      questions_quantity=questions_quantity, q_type=q_type)
        await questionnaire.create()
    except UniqueViolationError:
        print("Опрос уже существует")
        pass


async def select_questionnaire(quest_id: str):
    questionnaire = await Questionnaire.query.where(Questionnaire.quest_id == quest_id).gino.first()
    return questionnaire


async def increase_qe_started_by(quest_id: str):
    questionnaire = await select_questionnaire(quest_id=quest_id)
    started_by = questionnaire.started_by
    await questionnaire.update(started_by=started_by + 1).apply()


async def delete_questionnaire(quest_id: str):
    questionnaire = await select_questionnaire(quest_id=quest_id)

    qe_text_answers = await select_text_answers_tab(quest_id=quest_id)
    if qe_text_answers:
        for field in qe_text_answers:
            await field.delete()

    await questionnaire.delete()


async def freeze_questionnaire(quest_id: str, is_active: str):
    questionnaire = await select_questionnaire(quest_id=quest_id)
    await questionnaire.update(is_active=f"{is_active}").apply()


async def add_question(quest_id: str, question: str):
    questionnaire = await select_questionnaire(quest_id=quest_id)
    questions_arr = list(questionnaire.questions)
    questions_arr.append(question)
    await questionnaire.update(questions=questions_arr).apply()


async def create_qe_text_answers(respondent_id: int, quest_id: str, title: str, answers_quantity: int, ):
    try:
        qe_text_answers = QuestionnaireTextAnswers(respondent_id=respondent_id, quest_id=quest_id, title=title,
                                                   answers_quantity=answers_quantity)
        await qe_text_answers.create()
    except Exception as e:
        print(e)
        pass


async def select_qe_text_answers(respondent_id: int, quest_id: str):
    qe_text_answers = await QuestionnaireTextAnswers.query.where(and_(
        QuestionnaireTextAnswers.quest_id == quest_id,
        QuestionnaireTextAnswers.respondent_id == respondent_id)).gino.first()
    return qe_text_answers


async def select_text_answers_tab(quest_id: str):
    qe_text_answers_tab = await QuestionnaireTextAnswers.query.where(QuestionnaireTextAnswers.quest_id == quest_id).gino.all()
    return qe_text_answers_tab


async def delete_qe_text_answers(respondent_id: int, quest_id: str):
    qe_text_answers = await QuestionnaireTextAnswers.query.where(and_(
        QuestionnaireTextAnswers.quest_id == quest_id,
        QuestionnaireTextAnswers.respondent_id == respondent_id)).gino.first()
    await qe_text_answers.delete()


async def add_text_answer(respondent_id: int, quest_id: str, answer: str):
    qe_text_answers = await QuestionnaireTextAnswers.query.where(and_(
        QuestionnaireTextAnswers.quest_id == quest_id,
        QuestionnaireTextAnswers.respondent_id == respondent_id)).gino.first()
    answers_arr = list(qe_text_answers.answers)
    answers_arr.append(answer)
    await qe_text_answers.update(answers=answers_arr).apply()


async def update_complete_status(respondent_id: int, quest_id: str, status: str):
    qe_text_answers = await QuestionnaireTextAnswers.query.where(and_(
        QuestionnaireTextAnswers.quest_id == quest_id,
        QuestionnaireTextAnswers.respondent_id == respondent_id)).gino.first()
    is_completed = status
    await qe_text_answers.update(is_completed=is_completed).apply()


async def add_user_created_qe(creator_id: int, quest_id: str):
    user = await select_user(id=creator_id)
    created_qe = user.created_questionnaires
    created_qe.append(quest_id)
    await user.update(created_questionnaires=created_qe).apply()


async def remove_user_created_qe(creator_id: int, quest_id: str):
    user = await select_user(id=creator_id)
    created_qe = user.created_questionnaires
    created_qe.remove(quest_id)
    await user.update(created_questionnaires=created_qe).apply()


async def add_user_passed_qe(respondent_id: int, quest_id: str):
    user = await select_user(id=respondent_id)
    passed_qe = user.passed_questionnaires
    passed_qe.append(quest_id)
    await user.update(passed_questionnaires=passed_qe).apply()

    questionnaire = await select_questionnaire(quest_id=quest_id)
    passed_by = questionnaire.passed_by
    await questionnaire.update(passed_by=passed_by + 1).apply()


async def remove_user_passed_qe(respondent_id: int, quest_id: str):
    user = await select_user(id=respondent_id)
    passed_qe = user.passed_questionnaires
    passed_qe.remove(quest_id)
    await user.update(passed_questionnaires=passed_qe).apply()

    questionnaire = await select_questionnaire(quest_id=quest_id)
    passed_by = questionnaire.passed_by
    await questionnaire.update(passed_by=passed_by - 1).apply()
