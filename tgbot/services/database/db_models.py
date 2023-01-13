from sqlalchemy import Column, String, sql, ARRAY, Integer, Float

from tgbot.services.database.db_gino import TimeBaseModel, BaseModel


class User(TimeBaseModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))

    created_qe_quantity = Column(Integer, default=0)
    passed_qe_quantity = Column(Integer, default=0)

    query: sql.Select


class Questionnaire(TimeBaseModel):
    __tablename__ = "questionnaires"

    qe_id = Column(String(20), primary_key=True)
    creator_id = Column(Integer)

    title = Column(String(100))
    is_active = Column(String(10), default="true")
    started_by = Column(Integer, default=0)
    passed_by = Column(Integer, default=0)
    questions_quantity = Column(Integer, default=1)

    query: sql.Select


class Question(BaseModel):
    __tablename__ = "questions"

    question_id = Column(String(50), primary_key=True)
    qe_id = Column(String(20))

    question_type = Column(String(20))
    question_text = Column(String(250))

    query: sql.Select


class AnswerOption(BaseModel):
    __tablename__ = "answer_options"

    answer_option_id = Column(String(50), primary_key=True)
    question_id = Column(String(50))

    answer_option_text = Column(String(100))

    query: sql.Select


class UserAnswer(BaseModel):
    __tablename__ = "user_answers"

    answer_id = Column(String(50), primary_key=True)
    qe_id = Column(String(20))
    respondent_id = Column(Integer)

    answer_text = Column(String(500))

    query: sql.Select


class CreatedQuestionnaire(BaseModel):
    __tablename__ = "created_questionnaires"

    number = Column(Integer, primary_key=True, autoincrement=True)
    respondent_id = Column(Integer)
    qe_id = Column(String(20))

    query: sql.Select


class PassedQuestionnaire(BaseModel):
    __tablename__ = "passed_questionnaires"

    number = Column(Integer, primary_key=True, autoincrement=True)
    respondent_id = Column(Integer)
    qe_id = Column(String(20))

    completion_time = Column(Float, default=0)

    query: sql.Select
