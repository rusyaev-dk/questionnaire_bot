import openpyxl

from tgbot.services.database import db_commands
from tgbot.services.database.db_models import Questionnaire


async def create_xlsx_file(questionnaire: Questionnaire):
    title = questionnaire.title
    author = await db_commands.select_user(id=questionnaire.creator_id)

    questions_fields = await db_commands.select_questions(qe_id=questionnaire.qe_id)
    questions = []
    for field in questions_fields:
        questions.append(field.question_text)
    questions.insert(0, "№")

    wb = openpyxl.Workbook()
    table_list = wb.active
    table_list.append(questions)

    counter = 1
    passed_qes = await db_commands.select_passed_users(qe_id=questionnaire.qe_id)
    for passed_qe in passed_qes:
        answers_fields = await db_commands.select_user_answers(respondent_id=passed_qe.respondent_id,
                                                               qe_id=questionnaire.qe_id)
        answers = []
        for field in answers_fields:
            answers.append(field.answer_text)
        answers.insert(0, counter)
        table_list.append(answers)
        counter += 1


    table_list.append([f"Дата создания опроса: {questionnaire.created_at}"])
    table_list.append([f"Автор опроса: {author.name}"])

    # columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    # for i in range(quantity):
    #     table_list.row_dimensions[i].height = 40
    #     # table_list.column_dimensions[columns[i]] = 30

    path = f'D:\PycharmProjects\MSU_Questionnaire_Bot\\tgbot\services\Excel\excel_files\{title}.xlsx'
    wb.save(path)
    return path
