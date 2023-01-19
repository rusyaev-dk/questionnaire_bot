
from asyncpg import UniqueViolationError
from sqlalchemy import and_

from tgbot.services.database.db_gino import db
from tgbot.services.database.db_models import User, Questionnaire, Question, AnswerOption, UserAnswer, \
    PassedQuestionnaire, CreatedQuestionnaire

""" ____________Create functions____________ """


async def add_user(id: int, name: str):
    try:
        user = User(id=id, name=name)
        await user.create()
        return 0
    except UniqueViolationError:
        print("Пользователь уже есть в базе данных!")
        pass


async def create_questionnaire(qe_id: str, creator_id: int, title: str, questions_quantity: int):
    try:
        questionnaire = Questionnaire(qe_id=qe_id, creator_id=creator_id, title=title,
                                      questions_quantity=questions_quantity)
        await questionnaire.create()
    except UniqueViolationError:
        print("Опрос уже существует!")
        pass


async def create_question(question_id: str, qe_id: str, question_type: str, question_text: str):
    try:
        question = Question(question_id=question_id, qe_id=qe_id, question_type=question_type,
                            question_text=question_text)
        await question.create()
    except UniqueViolationError:
        print("Вопрос уже существует!")
        pass


async def create_answer_option(answer_option_id: str, question_id: str, answer_option_text: str):
    try:
        answer_option = AnswerOption(answer_option_id=answer_option_id, question_id=question_id,
                                     answer_option_text=answer_option_text)
        await answer_option.create()
    except UniqueViolationError:
        print("Вариант ответа уже существует!")
        pass


async def create_user_answer(answer_id: str, qe_id: str, respondent_id: int, answer_text: str):
    try:
        user_answer = UserAnswer(answer_id=answer_id, qe_id=qe_id, respondent_id=respondent_id, answer_text=answer_text)
        await user_answer.create()
    except UniqueViolationError:
        print("Ответ уже существует!")
        pass


async def add_created_qe(creator_id: int, qe_id: str):
    try:
        created = CreatedQuestionnaire(creator_id=creator_id, qe_id=qe_id)
        await created.create()
    except UniqueViolationError:
        print("Ошибка уникальности при создании опроса!")
        pass


async def add_passed_qe(respondent_id: int, qe_id: str, completion_time: float):
    try:
        passed_qe = PassedQuestionnaire(respondent_id=respondent_id, qe_id=qe_id, completion_time=completion_time)
        await passed_qe.create()
    except UniqueViolationError:
        print("Ошибка уникальности при прохождении опроса!")
        pass


""" ____________Select functions____________ """


async def select_user(id: int):
    user = await User.query.where(User.id == id).gino.first()
    return user


async def select_all_users():
    users = await User.query.gino.all()
    return users


async def select_questionnaire(qe_id: str):
    questionnaire = await Questionnaire.query.where(Questionnaire.qe_id == qe_id).gino.first()
    return questionnaire


async def select_questions(qe_id: str):
    questions = await Question.query.where(Question.qe_id == qe_id).gino.all()
    return questions


async def select_answer_options(question_id: str):
    answer_options = await AnswerOption.query.where(AnswerOption.question_id == question_id).gino.all()
    return answer_options


async def select_user_answers(respondent_id: int, qe_id: str):
    answers = await UserAnswer.query.where(and_(UserAnswer.respondent_id == respondent_id,
                                                UserAnswer.qe_id == qe_id)).gino.all()
    return answers


async def select_user_created_qes(creator_id: int):
    """
    Selects created questionnaires with respondent_id key
    """

    created_qes = await CreatedQuestionnaire.query.where(CreatedQuestionnaire.creator_id == creator_id).gino.all()
    return created_qes


async def select_user_passed_qes(respondent_id: int):
    """
    Selects passed questionnaires with respondent_id key
    """

    passed_qes = await PassedQuestionnaire.query.where(PassedQuestionnaire.respondent_id == respondent_id).gino.all()
    return passed_qes


async def select_passed_users(qe_id: str):
    """
    Selects users which passed questionnaires with qe_id key
    """

    passed_users = await PassedQuestionnaire.query.where(PassedQuestionnaire.qe_id == qe_id).gino.all()
    return passed_users


async def select_passed_qes(qe_id: str):
    """
    Selects passed questionnaires with qe_id key
    """
    passed_qes = await PassedQuestionnaire.query.where(PassedQuestionnaire.qe_id == qe_id).gino.all()
    return passed_qes


async def select_passed_qe(respondent_id: int, qe_id: str):
    passed_qe = await PassedQuestionnaire.query.where(and_(PassedQuestionnaire.respondent_id == respondent_id,
                                                           PassedQuestionnaire.qe_id == qe_id)).gino.first()
    return passed_qe


""" ____________Count functions____________ """


async def count_users():
    total = await db.func.count(User.id).gino.scalar()
    return total


async def count_qes():
    total = await db.func.count(Questionnaire.qe_id).gino.scalar()
    return total


""" ____________Delete functions____________ """


async def delete_questionnaire(qe_id: str):
    questionnaire = await select_questionnaire(qe_id=qe_id)
    questions = await select_questions(qe_id=qe_id)
    for question in questions:
        if question.question_type == "closed":
            answer_options = await select_answer_options(question_id=question.question_id)
            for option in answer_options:
                await option.delete()
        await question.delete()

    answers = await UserAnswer.query.where(UserAnswer.qe_id == qe_id).gino.all()
    for answer in answers:
        await answer.delete()

    created_qes = await CreatedQuestionnaire.query.where(CreatedQuestionnaire.qe_id == qe_id).gino.all()
    for created_qe in created_qes:
        await created_qe.delete()

    passed_qes = await PassedQuestionnaire.query.where(PassedQuestionnaire.qe_id == qe_id).gino.all()
    for passed_qe in passed_qes:
        await passed_qe.delete()

    await questionnaire.delete()


async def delete_user_answers(respondent_id: int, qe_id: str):
    user_answers = await select_user_answers(respondent_id=respondent_id, qe_id=qe_id)
    for answer in user_answers:
        await answer.delete()


async def delete_user_created_qe(creator_id: int, qe_id: str):
    created_qe = await CreatedQuestionnaire.query.where(and_(CreatedQuestionnaire.creator_id == creator_id,
                                                             CreatedQuestionnaire.qe_id == qe_id)).gino.first()
    await created_qe.delete()


async def delete_user_passed_qe(respondent_id: int, qe_id: str):
    passed_qe = await PassedQuestionnaire.query.where(and_(PassedQuestionnaire.respondent_id == respondent_id,
                                                           PassedQuestionnaire.qe_id == qe_id)).gino.first()
    await passed_qe.delete()


""" ____________Update functions____________ """


async def increase_qe_started_by(qe_id: str):
    questionnaire = await select_questionnaire(qe_id=qe_id)
    started_by = questionnaire.started_by
    await questionnaire.update(started_by=started_by + 1).apply()


async def decrease_qe_started_by(qe_id: str):
    questionnaire = await select_questionnaire(qe_id=qe_id)
    started_by = questionnaire.started_by
    await questionnaire.update(started_by=started_by - 1).apply()


async def increase_qe_passed_by(qe_id: str):
    questionnaire = await select_questionnaire(qe_id=qe_id)
    passed_by = questionnaire.passed_by
    await questionnaire.update(passed_by=passed_by + 1).apply()


async def decrease_passed_by(qe_id: str):
    questionnaire = await select_questionnaire(qe_id=qe_id)
    passed_by = questionnaire.passed_by
    await questionnaire.update(passed_by=passed_by - 1).apply()


async def freeze_questionnaire(qe_id: str, is_active: str):
    questionnaire = await select_questionnaire(qe_id=qe_id)
    await questionnaire.update(is_active=f"{is_active}").apply()


async def increase_user_passed_qe_quantity(respondent_id: int):
    """
    Passed questionnaires quantity for all time
    """
    user = await select_user(id=respondent_id)
    passed_qe_quantity = user.passed_qe_quantity
    await user.update(passed_qe_quantity=passed_qe_quantity + 1).apply()


async def increase_user_created_qe_quantity(creator_id: int):
    """
    Passed questionnaires quantity for all time
    """
    user = await select_user(id=creator_id)
    created_qe_quantity = user.created_qe_quantity
    await user.update(created_qe_quantity=created_qe_quantity + 1).apply()


async def increase_link_clicks(creator_id: int):
    user = await select_user(id=creator_id)
    link_clicks = user.link_clicks
    await user.update(link_clicks=link_clicks + 1).apply()


""" ____________Check functions____________ """


async def is_passed(respondent_id: int, qe_id: str):
    passed_qe = await PassedQuestionnaire.query.where(and_(PassedQuestionnaire.respondent_id == respondent_id,
                                                           PassedQuestionnaire.qe_id == qe_id)).gino.first()
    if passed_qe:
        return 1
    return 0
