from datetime import datetime

from house.basic.enum_tables import TableNames, TableId
from house.db.templates import MainModelTemplate, RowCreator, add_model_to_mapper
from sqlalchemy import func, SMALLINT, BIGINT, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from house.db.basic_types import tp_str_50, DTYPE_SERVERID, DTYPE_LOCALID, tp_server_timestamp, tp_str_5
from house.basic.enum_const import AppType

TABLE_NAME = TableNames.login


class LoginModel(MainModelTemplate):
    __tablename__ = TABLE_NAME.value
    __tableargs__ = (
        Index(TABLE_NAME.value + '_user_id_idx', 'user_id'),
        Index(TABLE_NAME.value + '_app_id_idx', 'sender_app_id'),
        Index(TABLE_NAME.value + '_phone_idx', 'country_code', 'phone_number'),
        MainModelTemplate.__table_args__
    )
    created_date: Mapped[datetime] = mapped_column(nullable=False, server_default=func.CURRENT_TIMESTAMP(),
                                                   comment="Время создания строки")
    id: Mapped[int] = mapped_column(DTYPE_SERVERID, primary_key=True, comment="ID Логина")
    local_id: Mapped[int] = mapped_column(DTYPE_LOCALID, nullable=False, comment="Локальный ID Логина")
    app_id: Mapped[int] = mapped_column(DTYPE_SERVERID, nullable=False, comment="ID приложения")
    app_type: Mapped[AppType] = mapped_column(nullable=False, comment="Тип приложения")
    user_id: Mapped[int] = mapped_column(DTYPE_SERVERID, nullable=True, comment="ID пользователя")
    new_user: Mapped[bool] = mapped_column(nullable=True, comment="Регистрация или вход в существующий аккаунт")

    country_code: Mapped[int] = mapped_column(SMALLINT, nullable=False, comment="Код страны")
    phone_number: Mapped[int] = mapped_column(BIGINT, nullable=False, index=True, comment="Номер телефона")

    sms_code: Mapped[int] = mapped_column(Integer, nullable=True, comment="Отправленный СМС-код")
    cnt_sms_tries: Mapped[int] = mapped_column(SMALLINT, nullable=True, comment="Кол-во попыток ввода последней смс")
    passed_sms: Mapped[bool] = mapped_column(nullable=True, comment="флаг, прошел смс верификацию ли логин")

    hashed_password: Mapped[tp_str_50] = mapped_column(nullable=True, comment="Hash пароля пользователя")
    salt: Mapped[tp_str_5] = mapped_column(nullable=True, comment="Salt для Hash-а")
    passed_password: Mapped[bool] = mapped_column(nullable=True, comment="флаг, прошел пользовательский пароль")

    success: Mapped[bool] = mapped_column(nullable=True, comment="флаг, успешный ли логин")
    finish_datetime: Mapped[datetime] = mapped_column(nullable=True, comment="дата проставления флага success")
    reason: Mapped[str] = mapped_column(nullable=True, comment="Описание причины почему success = False")
    wait_minutes: Mapped[int] = mapped_column(nullable=True, comment="Скольно минут недоступен ближайший логин")

    # TODO: Подумать над уникальным ключом для sender_app_id local_id
    @property
    def row_id(self) -> int:
        return self.id

    @property
    def row_creator(self) -> RowCreator:
        return RowCreator(self.app_id, None)

    # : Mapped["AppModel"], TableNames.application.value,
    # : Mapped["UserModel"]
    application: Mapped["AppModel"] = relationship(
        'AppModel',
        primaryjoin='LoginModel.sender_app_id == AppModel.id',
        back_populates='logins',
        foreign_keys=app_id,
    )

    user: Mapped["UserModel"] = relationship(
        'UserModel',
        primaryjoin='LoginModel.user_id == UserModel.id',
        back_populates='logins',
        foreign_keys=user_id,
    )


add_model_to_mapper(TableId.login, LoginModel)
