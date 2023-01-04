import random, string

from tgbot.services.database import db_commands


def get_rand_id(length):
    letters = string.ascii_lowercase + string.ascii_uppercase
    digits = string.digits
    symbols = letters + digits
    return ''.join(random.choice(symbols) for i in range(length))


async def parse_questions_text(questionnaire):
    questions_list = questionnaire.questions
    text = "🔍 Ваш опрос:\n\n" + f"🔹 Название: <b>{questionnaire.title}</b>\n\n" + "\n".join(
        f"Вопрос {i + 1}: <b>{questions_list[i]}</b>" for i in range(0, len(questions_list))
    ) + "\n\nСоздать опрос?"
    return text


async def parse_answers_text(qe_text_answers):
    answers_list = list(qe_text_answers.answers)
    text = "✏️ Ваши ответы:\n" + "\n".join(f"Ответ {i + 1}: <b>{answers_list[i]}</b>"
                                        for i in range(0, len(answers_list)))
    return text


async def get_created_questionnaire_info(questionnaire):
    questions_list = list(questionnaire.questions)
    text = f"🔍 Название: <b>{questionnaire.title}</b>\n\n" + "\n".join(f"Вопрос {i + 1}: <b>{questions_list[i]}</b>"
                                                                         for i in range(0, len(questions_list)))
    try:
        pass_percent = questionnaire.started_by / questionnaire.passed_by * 100
    except ZeroDivisionError:
        pass_percent = 0
        pass
    stat_text = (f"\n\n📊 Статистика:\n"
                 f"• Начали проходить: <b>{questionnaire.started_by}</b> чел.\n"
                 f"• Прошли: <b>{questionnaire.passed_by}</b> чел.\n"
                 f"• Процент прохождения: <b>{pass_percent}%</b>\n"
                 f"• Дата создания: <b>{questionnaire.created_at}</b>")
    text += stat_text
    return text


async def get_passed_questionnaire_info(respondent_id: int, quest_id: str, markdown: bool):
    questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
    questions_list = list(questionnaire.questions)
    qe_text_answers = await db_commands.select_qe_text_answers(respondent_id=respondent_id, quest_id=quest_id)
    answers_list = list(qe_text_answers.answers)

    if markdown:
        text = f"🔹 Название: **{qe_text_answers.title}**\n\n" + "\n".join(
            f"Вопрос {i + 1}: **{questions_list[i]}**\n"
            f"Ответ: **{answers_list[i]}**\n"
            for i in range(0, len(questions_list)))
        text += f"\nДата прохождения: **{qe_text_answers.created_at}**"
    else:
        text = f"🔹 Название: <b>{qe_text_answers.title}</b>\n\n" + "\n".join(f"Вопрос {i + 1}: <b>{questions_list[i]}</b>\n"
                                                                             f"Ответ: <b>{answers_list[i]}</b>\n"
                                                                             for i in range(0, len(questions_list)))
        text += f"\nДата прохождения: <b>{qe_text_answers.created_at}</b>"
    return text
