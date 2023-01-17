from sqlalchemy import Column, String, sql, Integer, Float, BigInteger

from tgbot.services.database.db_gino import TimeBaseModel, BaseModel
from tgbot.misc.dependences import TITLE_LENGTH, QUESTION_LENGTH, ANSWER_OPTION_LENGTH, ANSWER_LENGTH, QE_ID_LENGTH, \
    QUESTION_ID_LENGTH, ANSWER_OPTION_ID_LENGTH, USER_ANSWER_ID_LENGTH


class User(TimeBaseModel):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    name = Column(String(70))

    created_qe_quantity = Column(Integer, default=0)
    passed_qe_quantity = Column(Integer, default=0)

    link_clicks = Column(Integer, default=0)

    query: sql.Select


class Questionnaire(TimeBaseModel):
    __tablename__ = "questionnaires"

    qe_id = Column(String(QE_ID_LENGTH), primary_key=True)
    creator_id = Column(BigInteger)

    title = Column(String(TITLE_LENGTH))
    is_active = Column(String(10), default="true")
    started_by = Column(Integer, default=0)
    passed_by = Column(Integer, default=0)
    questions_quantity = Column(Integer, default=1)

    query: sql.Select


class Question(BaseModel):
    __tablename__ = "questions"

    question_id = Column(String(QUESTION_ID_LENGTH), primary_key=True)
    qe_id = Column(String(QE_ID_LENGTH))

    question_type = Column(String(10))
    question_text = Column(String(QUESTION_LENGTH))

    query: sql.Select


class AnswerOption(BaseModel):
    __tablename__ = "answer_options"

    answer_option_id = Column(String(ANSWER_OPTION_ID_LENGTH), primary_key=True)
    question_id = Column(String(QE_ID_LENGTH))

    answer_option_text = Column(String(ANSWER_OPTION_LENGTH))

    query: sql.Select


class UserAnswer(BaseModel):
    __tablename__ = "user_answers"

    answer_id = Column(String(USER_ANSWER_ID_LENGTH), primary_key=True)
    qe_id = Column(String(QE_ID_LENGTH))
    respondent_id = Column(BigInteger)

    answer_text = Column(String(ANSWER_LENGTH))

    query: sql.Select


class CreatedQuestionnaire(BaseModel):
    __tablename__ = "created_questionnaires"

    number = Column(Integer, primary_key=True, autoincrement=True)
    creator_id = Column(BigInteger)
    qe_id = Column(String(QE_ID_LENGTH))

    query: sql.Select


class PassedQuestionnaire(BaseModel):
    __tablename__ = "passed_questionnaires"

    number = Column(Integer, primary_key=True, autoincrement=True)
    respondent_id = Column(BigInteger)
    qe_id = Column(String(QE_ID_LENGTH))

    completion_time = Column(Float, default=0)

    query: sql.Select
