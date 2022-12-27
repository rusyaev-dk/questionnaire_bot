from sqlalchemy import Column, BigInteger, String, sql, ARRAY, Integer

from tgbot.services.database.db_gino import TimeBaseModel, BaseModel


class User(TimeBaseModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    user_questionnaires = Column(ARRAY(String(500)), default=[])
    name = Column(String(100))

    query: sql.Select


class Questionnaire(BaseModel):
    __tablename__ = "questionnaires"

    quest_id = Column(String, primary_key=True)
    creator_id = Column(Integer)
    title = Column(String(100))
    questions_quantity = Column(Integer, default=1)
    questions = Column(ARRAY(String(500)), default=[])

    query: sql.Select


class QuestionnaireTextAnswers(BaseModel):
    __tablename__ = "q_text_answers"

    num = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100))
    is_completed = Column(String(5), default="false")
    quest_id = Column(String)
    respondent_id = Column(Integer)
    answers_quantity = Column(Integer)
    answers = Column(ARRAY(String(2000)), default=[])

    query: sql.Select
