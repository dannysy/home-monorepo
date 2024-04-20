from typing import List, Tuple

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from house.validation.general import valid_app


async def valid_create_login(msg: CreateLoginSchema, session: AsyncSession) -> bool:
    """
    Проверка на возможность создания объекта логина.
    """
    # TODO: Необходимо добавить проверку на возможность создания объекта логина для устройства/номера.
    return True


async def valid_update_login(msg: LoginSMSSchema | LoginPswrdSchema,
                             session: AsyncSession,
                             ) -> LoginModel:
    """
    Проверка на возможность изменения объекта логина = возможность дальше проходить процедуру входа в аккаунт.
    """
    login_obj = (await session.execute(
        select(LoginModel).
        where(LoginModel.id == msg.id).
        where(LoginModel.sender_app_id == msg.sender_app_id).
        where(LoginModel.success == None)
    )).scalar()
    if login_obj is None:
        raise OldLoginError()
    elif login_obj.success is not None:
        raise LoginSpentError()
    elif type(msg) is LoginSMSSchema and login_obj.passed_sms:
        raise WrongLoginRequest()
    elif type(msg) is LoginPswrdSchema and not login_obj.passed_sms:
        raise WrongLoginRequest()

    # TODO: Необходимо добавить проверку на возможность дальнейшего прохождения логина для устройства/номера.
    return login_obj

