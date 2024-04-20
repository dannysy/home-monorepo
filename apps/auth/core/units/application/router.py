from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.data_base.database import get_session
from core.validators import valid_app
from .crud import CRUDapp
from .schema import ReceivedAppReg, SendAppReg, ReceivedAppUpd

router = APIRouter(prefix="/app")

# TODO: Нужно отдавать какой-то ответ на случай ошибок внутри CRUDD


@router.post("/register")
async def register_app(msg: ReceivedAppReg, session: AsyncSession = Depends(get_session)) -> SendAppReg:
    # TODO: Необходимо добавить какой-то валидатор, а то будут спамить и спокойно создавать App
    send_app_reg = await CRUDapp.create(msg, session)

    # TODO: Как поставить обработчик, на случай если мы не смогли передать id устройства юзеру? По идее необходимо
    #  удалить зарегистрированное устройство из нашей БД, так как пользователь опять придет с регистрацией приложения.
    return send_app_reg  # SendAppReg(id=1)  # send_app_reg


@router.post("/update")
async def update_app(msg: ReceivedAppUpd, session: AsyncSession = Depends(get_session),
                     valid_app: bool = Depends(valid_app)) -> None:
    # TODO: Как ограничить доступ к этому методу.
    #  Сейчас все кто хочет может присылать апдейты даже не на свои устройства
    await CRUDapp.update(msg, session)
