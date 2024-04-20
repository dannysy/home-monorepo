from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.auth.core.units.login.schema import ReceivedCreateLogin
from data_base.database import get_session

router = APIRouter(prefix="/login")


@router.post('create')
async def create_login(msg: ReceivedCreateLogin, session: AsyncSession = Depends(get_session),
                       valid_login: bool = Depends(valid_create_login)) -> None:

    # TODO: Валидатор на создание объекта логина. Доступно ли это создание.
    #  Но в CRUDlogin.create также идет валидация на возможность логина...
    await valid_create_login(msg, session)
    await CRUDlogin(session).create(msg)


async def ws_verify_sms_code(msg: dict, session: AsyncSession):
    msg = LoginSMSSchema(**msg)
    try:
        login: LoginModel = await valid_update_login(msg, session)
    except (OldLoginError, LoginSpentError, WrongLoginRequest) as e:
        raise BadRequestException()

    await CRUDlogin(session).verify_sms_code(login, msg)


async def ws_verify_password(msg: dict, session: AsyncSession):
    msg = LoginPswrdSchema(**msg)
    try:
        login: LoginModel = await valid_update_login(msg, session)
    except (OldLoginError, LoginSpentError, WrongLoginRequest) as e:
        raise BadRequestException()
    await CRUDlogin(session).verify_pswrd(login, msg)


async def ws_login_router(msg: dict, session: AsyncSession):
    if msg['_endpoint'] == LoginRouts.create:
        await ws_create_login(msg, session)
    elif msg['_endpoint'] == LoginRouts.verify_sms:
        await ws_verify_sms_code(msg, session)
    elif msg['_endpoint'] == LoginRouts.verify_pswrd:
        await ws_verify_password(msg, session)
    else:
        raise BadRequestException()
