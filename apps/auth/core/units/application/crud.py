from datetime import datetime, UTC
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from .schema import ReceivedAppReg, SendAppReg, ReceivedAppUpd
from .model import AppModel, HistoryAppModel
from core.in_memory.app_status import add_reged_app, add_notreged_app


class CRUDapp:

    @classmethod
    async def create(cls, msg: ReceivedAppReg, session: AsyncSession) -> SendAppReg:
        obj = AppModel(
            app_type=msg.app_type,
            app_version=msg.app_version,
            device_info=msg.device_info
        )
        session.add(obj)
        await session.commit()
        add_reged_app(obj.id)  # Добавили зарегистрированное устройство в InMemory хранилище
        return SendAppReg.model_validate(obj)

    @classmethod
    async def delete(cls, app_id: int, session: AsyncSession) -> None:
        await session.execute(delete(AppModel).where(AppModel.id == app_id))
        await session.execute(delete(HistoryAppModel).where(HistoryAppModel.id == app_id))
        # Добавили НЕзарегистрированное устройство в InMemory хранилище, удаляет из зарегистрированных
        add_notreged_app(app_id)
        await session.commit()

    @classmethod
    async def update(cls, msg: ReceivedAppUpd, session: AsyncSession):
        app = (await session.execute(select(AppModel).where(AppModel.id == msg.sender_app_id))).scalar()

        if msg.device_info is not None:
            app.device_info = msg.device_info

        if msg.app_version is not None:
            app.app_version = msg.app_version
            app.update_date = datetime.now(UTC)

        session.add(app)
        await session.commit()
