from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.data_base.database import get_session
from core.in_memory.app_status import is_reged_app, add_reged_app
from core.schema import ReceivedBasic
from core.units.application.model import AppModel


async def valid_app(msg: ReceivedBasic, session: AsyncSession = Depends(get_session)):
    status = is_reged_app(msg.sender_app_id)
    if status:
        return True
    elif status is False:
        raise HTTPException(status_code=400, detail="Wrong sender_app_id")
    else:
        app = (await session.execute(
            select(AppModel).
            where(AppModel.id == msg.sender_app_id)
        )).scalar()
        if app is None:
            raise HTTPException(status_code=400, detail="Wrong sender_app_id")
        else:
            add_reged_app(msg.sender_app_id)
            return True
