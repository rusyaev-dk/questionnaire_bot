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

        user = await select_user(creator_id)
        quest_id_arr = list(user.created_questionnaires)
        quest_id_arr.append(quest_id)
        await user.update(created_questionnaires=quest_id_arr).apply()

    except UniqueViolationError:
        print("Опрос уже существует")
        pass


async def select_questionnaire(quest_id: str):
    questionnaire = await Questionnaire.query.where(Questionnaire.quest_id == quest_id).gino.first()
    return questionnaire


async def increase_started_by(quest_id: str):
    questionnaire = await select_questionnaire(quest_id=quest_id)
    started_by = questionnaire.started_by
    await questionnaire.update(started_by=started_by + 1).apply()


async def delete_questionnaire(creator_id: int, quest_id: str):
    questionnaire = await select_questionnaire(quest_id=quest_id)
    user = await select_user(creator_id)

    qe_text_answers = await select_all_qe_text_answers(quest_id=quest_id)
    for field in qe_text_answers:
        await field.delete()

    created_qe = list(user.created_questionnaires)
    created_qe.remove(f"{quest_id}")

    passed_qe = list(user.passed_questionnaires)
    passed_qe.remove(f"{quest_id}")

    await user.update(created_questionnaires=created_qe).apply()
    await user.update(passed_questionnaires=passed_qe).apply()
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


async def select_qe_text_answers(quest_id: str, respondent_id: int):
    qe_text_answers = await QuestionnaireTextAnswers.query.where(and_(
        QuestionnaireTextAnswers.quest_id == quest_id,
        QuestionnaireTextAnswers.respondent_id == respondent_id)).gino.first()
    return qe_text_answers


async def select_all_qe_text_answers(quest_id: str):
    qe_text_answers_tab = await QuestionnaireTextAnswers.query.where(QuestionnaireTextAnswers.quest_id == quest_id).gino.all()
    return qe_text_answers_tab


async def delete_qe_text_answers(quest_id: str, respondent_id: int):
    qe_text_answers = await QuestionnaireTextAnswers.query.where(and_(
        QuestionnaireTextAnswers.quest_id == quest_id,
        QuestionnaireTextAnswers.respondent_id == respondent_id)).gino.first()
    await qe_text_answers.delete()


async def add_text_answer(quest_id: str, respondent_id: int, answer: str):
    qe_text_answers = await QuestionnaireTextAnswers.query.where(and_(
        QuestionnaireTextAnswers.quest_id == quest_id,
        QuestionnaireTextAnswers.respondent_id == respondent_id)).gino.first()
    answers_arr = list(qe_text_answers.answers)
    answers_arr.append(answer)
    await qe_text_answers.update(answers=answers_arr).apply()


async def set_complete_status(quest_id: str, respondent_id: int, status: str):
    qe_text_answers = await QuestionnaireTextAnswers.query.where(and_(
        QuestionnaireTextAnswers.quest_id == quest_id,
        QuestionnaireTextAnswers.respondent_id == respondent_id)).gino.first()
    is_completed = status
    await qe_text_answers.update(is_completed=is_completed).apply()


async def add_passed_qe(id: int, quest_id: str):
    user = await select_user(id=id)
    passed_questionnaires = list(user.passed_questionnaires)
    passed_questionnaires.append(quest_id)
    await user.update(passed_questionnaires=passed_questionnaires).apply()

    questionnaire = await select_questionnaire(quest_id=quest_id)
    passed_by = questionnaire.passed_by
    await questionnaire.update(passed_by=passed_by+1).apply()


async def remove_passed_qe(quest_id: str, respondent_id: int):
    user = await select_user(id=respondent_id)
    passed_qe = user.passed_questionnaires
    passed_qe.remove(f"{quest_id}")

    await user.update(passed_questionnaires=passed_qe).apply()
