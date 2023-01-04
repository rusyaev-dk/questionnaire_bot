import openpyxl

from tgbot.services.database import db_commands


async def create_xlsx_file(qe_text_answers_tab: list, quest_id: str):
    questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
    title = questionnaire.title
    author = await db_commands.select_user(id=questionnaire.creator_id)
    quantity = questionnaire.passed_by
    questions = questionnaire.questions

    questions.insert(0, "№")

    wb = openpyxl.Workbook()
    table_list = wb.active
    table_list.append(questions)

    counter = 1
    for field in qe_text_answers_tab:
        qe_text_answers = await db_commands.select_qe_text_answers(quest_id=quest_id, respondent_id=field.respondent_id)
        answers = qe_text_answers.answers
        answers.insert(0, counter)
        table_list.append(answers)
        counter += 1

    table_list.append([f"Дата создания опроса: {questionnaire.created_at}"])
    table_list.append([f"Автор опроса: {author.name}"])

    # columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    # for i in range(quantity):
    #     table_list.row_dimensions[i].height = 40
    #     # table_list.column_dimensions[columns[i]] = 30

    path = f'D:\PycharmProjects\MSU_Questionnaire_Bot\\tgbot\services\Excel\Excel_files\{title}.xlsx'
    wb.save(path)
    return path
