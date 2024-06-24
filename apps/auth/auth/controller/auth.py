from datetime import timedelta, datetime
import random

import re
from typing import Annotated

from auth.repository.db import User, Session
from sqlalchemy import or_, cast, TEXT
from fastapi import Response, Request, Form, APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from auth import config as app_config
from jose import JWTError, jwt
from auth.client import redis
from .contracts import Token
from passlib.context import CryptContext

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(prefix="", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(wildcard_id: str) -> User | None:
    session = Session()
    user = (
        session.query(User)
        .filter(or_(User.email == wildcard_id, User.phone == wildcard_id, cast(User.id, TEXT).like(wildcard_id)))
        .one_or_none()
    )
    session.close()
    return user


def authenticate_user(wildcard_id: str, password: str) -> User | None:
    user = get_user(wildcard_id)
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_tokens(user_id: str) -> tuple[str, str]:
    access_data = {"sub": user_id, "exp": datetime.now() + timedelta(seconds=900)}
    refresh_data = {"sub": user_id, "exp": datetime.now() + timedelta(seconds=86400)}
    access_token = jwt.encode(access_data, app_config.Config.AUTH_JWT_SECRET, algorithm="HS256")
    refresh_token = jwt.encode(refresh_data, app_config.Config.AUTH_JWT_SECRET, algorithm="HS256")
    redis.gist.setex(access_token, 900, user_id)
    redis.gist.setex(refresh_token, 86400, access_token)
    return access_token, refresh_token


# TODO тут либо отправка СМС с кодами либо whatsapp добить
@router.post("/authorize")
async def authorize(phone: str):
    session = Session()
    user_exists = session.query(session.query(User).filter(User.phone == phone).exists()).scalar()
    if not user_exists:
        user = User()
        user.phone = phone
        session.add(user)
        session.commit()
        session.close()
    code = (
        str(random.randint(0, 9))
        + str(random.randint(0, 9))
        + str(random.randint(0, 9))
        + str(random.randint(0, 9))
        + str(random.randint(0, 9))
        + str(random.randint(0, 9))
    )
    redis.gist.setex(phone, 60, code)
    # TODO
    # chatId = phone + "@c.us"
    # response = green_api.gist.sending.sendMessage(chatId, code)
    # if response.code != 200:
    #     raise HTTPException(status_code=response.code, detail=response.data)
    return code

@router.post("/validate")
async def validate(req: Request, response: Response):
    token = req.headers["Authorization"]
    try:
        payload = jwt.decode(token, app_config.Config.AUTH_JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        response.headers["X-User-ID"] = user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return

@router.post("/register")
async def register_user(phone: str, password: str, fio: str | None = None, email: str | None = None):
    session = Session()
    user_exists = session.query(session.query(User).filter(User.phone == phone).exists()).scalar()
    if user_exists:
        raise HTTPException(status_code=400, detail="User already exists")
    user = User()
    user.hashed_password = pwd_context.hash(password)
    user.phone = phone
    user.fio = fio
    user.email = email
    session.add(user)
    session.commit()
    session.close()
    return {"message": "User registered"}

@router.post("/token")
async def token(
    grant_type: Annotated[str, Form()],
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    refresh_token: Annotated[str, Form()] | None = None,
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    match grant_type:
        case "refresh_token":
            try:
                payload = jwt.decode(refresh_token, app_config.Config.AUTH_JWT_SECRET, algorithms=["HS256"])
                user_id = payload.get("sub")
                access_token = redis.gist.getdel(refresh_token)
                redis.gist.delete(access_token)
                access_token, refresh_token = create_tokens(user_id=user_id)
                return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")
            except JWTError:
                raise credentials_exception
        case "password":
            code = redis.gist.getdel(username)
            if code == password:
                user = get_user(username)
                access_token, refresh_token = create_tokens(user_id=user.id.hex)
                return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")
            user = authenticate_user(username, password)
            if user is None:
                raise credentials_exception
            access_token, refresh_token = create_tokens(user_id=user.id.hex)
            return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")
        case _:
            raise HTTPException(status_code=400, detail="Bad request")


@router.get("/users/me/")
async def read_users_me(
    access_token: Annotated[str, Depends(oauth2_scheme)],
):
    payload = jwt.decode(access_token, app_config.Config.AUTH_JWT_SECRET, algorithms=["HS256"])
    user_id = payload.get("sub")
    uuid_user_id = re.sub(r"(\S{8})(\S{4})(\S{4})(\S{4})(.*)", r"\1-\2-\3-\4-\5", user_id)
    user = get_user(uuid_user_id)
    return user.fio
