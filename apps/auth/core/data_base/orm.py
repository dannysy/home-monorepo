from datetime import datetime
from typing import Annotated

from sqlalchemy import String, TIMESTAMP, Date, Boolean, SMALLINT, func, BIGINT
import sqlalchemy.types as types
from sqlalchemy.orm import registry, mapped_column

from core.const import AppType
from core.data_base.database import Base

tp_str_5 = Annotated[str, 10]
tp_str_10 = Annotated[str, 10]
tp_str_15 = Annotated[str, 15]
tp_str_30 = Annotated[str, 30]
tp_str_32 = Annotated[str, 32]
tp_str_50 = Annotated[str, 50]
tp_str_64 = Annotated[str, 64]
tp_str_200 = Annotated[str, 200]

annotation_map = {
    tp_str_15: String(15),
    tp_str_30: String(30),
    tp_str_50: String(50),
    tp_str_64: String(64),
    tp_str_200: String(200),
    datetime: TIMESTAMP,
    datetime.date: Date,
    bool: Boolean
}

tp_server_timestamp = Annotated[
    datetime,
    mapped_column(nullable=False, server_default=func.CURRENT_TIMESTAMP(),
                  comment="Время последней манипуляции строкой")
]
tp_server_timestamp_primary = mapped_column(nullable=False, primary_key=True,  server_default=func.CURRENT_TIMESTAMP(),
                                            comment="Время последней манипуляции строкой")

DTYPE_SERVERID = BIGINT


class IntEnum(types.TypeDecorator):
    """
    Enables passing in a Python enum and storing the enum's *value* in the db.
    The default would have stored the enum's *name* (ie the string).
    """
    impl = SMALLINT

    def __init__(self, enumtype, *args, **kwargs):
        super(IntEnum, self).__init__(*args, **kwargs)
        self._enumtype = enumtype

    def process_bind_param(self, value, dialect):
        if isinstance(value, int):
            return value
        if value is None:
            return None
        else:
            return value.value

    def process_result_value(self, value, dialect):
        return self._enumtype(value)


class CoreOrmTemplate(Base):
    __abstract__ = True

    registry = registry(
        type_annotation_map={**annotation_map, **{
            AppType: IntEnum(AppType)
        }}
    )


MAIN_SCHEMA = 'auth_main'
HISTORY_SCHEMA = 'auth_history'
