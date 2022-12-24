from typing import List

from aiogram import Dispatcher
from gino import Gino
import sqlalchemy as sa
from sqlalchemy import Integer, Column, String, DateTime

import tgbot.config

POSTGRES_URI = f"postgresql://{tgbot.config.load_config().db.user}:{tgbot.config.load_config().db.password}" \
               f"@{tgbot.config.load_config().db.host}/{tgbot.config.load_config().db.database}"

db = Gino()


class BaseModel(db.Model):
    __abstract__ = True

    def __str__(self):
        model = self.__class__.__name__
        table: sa.Table = sa.inspect(self.__class__)
        primary_key_columns: List[sa.Column] = table.columns
        values = {
            column.name: getattr(self, self._column_name_map[column.name])
            for column in primary_key_columns
        }
        values_str = " ".join(f"{name}={value!r}" for name, value in values.items())
        return f"<{model} {values_str}>"


class TimeBaseModel(BaseModel):
    __abstract__ = True
    created_at = Column(DateTime(True), server_default=db.func.now())
    updated_at = Column(DateTime(True),
                        default=db.func.now(),
                        onupdate=db.func.now(),
                        server_default=db.func.now())


async def on_startup(dp: Dispatcher):
    print("Устанавливаем связи с PostgreSQL")
    await db.set_bind(POSTGRES_URI)
