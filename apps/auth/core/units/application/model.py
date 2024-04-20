from datetime import datetime
from typing import List

from sqlalchemy import event, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.const import TableNames, AppType
from core.data_base.orm import CoreOrmTemplate, tp_server_timestamp, DTYPE_SERVERID, tp_str_50, \
    tp_server_timestamp_primary, MAIN_SCHEMA, HISTORY_SCHEMA
from core.data_base.triggers import trigger_upd_server_time, trf_insert_to_hist, trigger_to_history

TABLE_NAME = TableNames.application


class TemplateModel(CoreOrmTemplate):
    __abstract__ = True

    created_date: Mapped[datetime] = mapped_column(nullable=False, server_default=func.CURRENT_TIMESTAMP(),
                                                   comment="Время создания строки")
    server_time: Mapped[tp_server_timestamp]
    id: Mapped[int] = mapped_column(DTYPE_SERVERID, primary_key=True, comment="ID приложения")
    app_type: Mapped[AppType] = mapped_column(nullable=False, comment="Тип приложения")
    app_version: Mapped[int] = mapped_column(nullable=False, comment="версия приложения")
    device_info: Mapped[tp_str_50] = mapped_column(nullable=False, comment="информация об устройстве")



class AppModel(TemplateModel):
    __tablename__ = TABLE_NAME.value
    __table_args__ = {"schema": MAIN_SCHEMA}

    # logins: Mapped[List["LoginModel"]] = relationship(back_populates="application")


class HistoryAppModel(TemplateModel):
    __tablename__ = TABLE_NAME.value
    __table_args__ = {"schema": HISTORY_SCHEMA}
    server_time: Mapped[datetime] = tp_server_timestamp_primary


updated_cols = [
    AppModel.app_version.key,
    AppModel.device_info.key,
]

# Будет апдейтить server_time у записи при изменении значений в updated_cols
tr_update = trigger_upd_server_time(AppModel, include_cols=updated_cols)
event.listen(AppModel.__table__, "after_create", tr_update.execute_if(dialect="postgresql"))

# Функция переноса данных из обычной таблицы в историческую
trf_history = trf_insert_to_hist(AppModel, HistoryAppModel)
event.listen(AppModel.__table__, "after_create", trf_history.execute_if(dialect="postgresql"))

# Регистрируем триггер, который будет вызывать функцию копирования строки в историческую таблицу
tr_history = trigger_to_history(AppModel, include_cols=updated_cols)
event.listen(AppModel.__table__, "after_create", tr_history.execute_if(dialect="postgresql"))
