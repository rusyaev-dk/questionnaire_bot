from datetime import date

from sqlalchemy import Column, String, sql, Integer, Float, BigInteger

from tgbot.services.database.db_gino import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    name = Column(String(70))

    created_qe_quantity = Column(Integer, default=0)
    passed_qe_quantity = Column(Integer, default=0)

    link_clicks = Column(Integer, default=0)

    query: sql.Select


class Questionnaire(BaseModel):
    __tablename__ = "questionnaires"

    qe_id = Column(String(10), primary_key=True)
    creator_id = Column(BigInteger)

    title = Column(String(30))
    is_active = Column(String(10), default="true")
    started_by = Column(Integer, default=0)
    passed_by = Column(Integer, default=0)
    questions_quantity = Column(Integer, default=1)

    created_at = Column(String(15), default=f"{date.today()}")

    query: sql.Select


class Question(BaseModel):
    __tablename__ = "questions"

    question_id = Column(String(20), primary_key=True)
    qe_id = Column(String(10))

    question_type = Column(String(10))
    question_text = Column(String(350))

    query: sql.Select


class AnswerOption(BaseModel):
    __tablename__ = "answer_options"

    answer_option_id = Column(String(20), primary_key=True)
    question_id = Column(String(20))

    answer_option_text = Column(String(100))

    query: sql.Select


class UserAnswer(BaseModel):
    __tablename__ = "user_answers"

    answer_id = Column(String(20), primary_key=True)
    qe_id = Column(String(10))
    respondent_id = Column(BigInteger)

    answer_text = Column(String(2000))
    answer_time = Column(Float)

    query: sql.Select


class CreatedQuestionnaire(BaseModel):
    __tablename__ = "created_questionnaires"

    number = Column(Integer, primary_key=True, autoincrement=True)
    creator_id = Column(BigInteger)
    qe_id = Column(String(10))

    query: sql.Select


class PassedQuestionnaire(BaseModel):
    __tablename__ = "passed_questionnaires"

    number = Column(Integer, primary_key=True, autoincrement=True)
    respondent_id = Column(BigInteger)
    qe_id = Column(String(10))

    completion_time = Column(Float, default=0)
    passed_at = Column(String(15), default=f"{date.today()}")

    query: sql.Select
