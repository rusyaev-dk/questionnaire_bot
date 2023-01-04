from sqlalchemy import Column, String, sql, ARRAY, Integer

from tgbot.services.database.db_gino import TimeBaseModel, BaseModel


class User(TimeBaseModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))

    created_questionnaires = Column(ARRAY(String(500)), default=[])
    passed_questionnaires = Column(ARRAY(String(2000)), default=[])

    query: sql.Select


class Questionnaire(TimeBaseModel):
    __tablename__ = "questionnaires"

    quest_id = Column(String, primary_key=True)
    creator_id = Column(Integer)

    q_type = Column(String(10))
    title = Column(String(100))

    is_active = Column(String(10), default="true")

    started_by = Column(Integer, default=0)
    passed_by = Column(Integer, default=0)

    questions_quantity = Column(Integer, default=1)
    questions = Column(ARRAY(String(500)), default=[])

    query: sql.Select


class QuestionnaireTextAnswers(TimeBaseModel):
    __tablename__ = "q_text_answers"

    num = Column(Integer, primary_key=True, autoincrement=True)
    respondent_id = Column(Integer)
    quest_id = Column(String)

    title = Column(String(100))
    is_completed = Column(String(5), default="false")

    answers_quantity = Column(Integer)
    answers = Column(ARRAY(String(2000)), default=[])

    query: sql.Select
