import random, string


def get_rand_id(length):
    letters = string.ascii_lowercase + string.ascii_uppercase
    digits = string.digits
    symbols = letters + digits
    return ''.join(random.choice(symbols) for i in range(length))


async def parse_questions_text(questionnaire):
    questions_list = questionnaire.questions
    text = "Ваш опрос:\n\n" + f"Название: <b>{questionnaire.title}</b>\n" + "\n".join(
        f"<b>Вопрос {i + 1}: </b>{questions_list[i]}" for i in range(0, len(questions_list))
    ) + "\n\nСоздать опрос?"
    return text


async def get_questionnaire_info(questionnaire):
    questions_list = questionnaire.questions
    text = f"Название: <b>{questionnaire.title}</b>\n" + "\n".join(f"<b>Вопрос {i + 1}: </b>{questions_list[i]}"
                                                                   for i in range(0, len(questions_list)))
    return text
