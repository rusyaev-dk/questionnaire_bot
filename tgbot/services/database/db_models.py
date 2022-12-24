from sqlalchemy import Column, BigInteger, String, sql, ARRAY, Integer

from tgbot.services.database.db_gino import TimeBaseModel, BaseModel


class User(TimeBaseModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
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
