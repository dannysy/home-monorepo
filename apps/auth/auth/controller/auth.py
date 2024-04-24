from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_jwt import JwtAccessBearerCookie, JwtRefreshBearerCookie
from ..config import AppConfig
from passlib.context import CryptContext
from .models import TokenRequest, TokenResponse

router = APIRouter(prefix="", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
access_security = JwtAccessBearerCookie(
    secret_key="secret",  # TODO Replace with real secret from config
    auto_error=False,
    access_expires_delta=900,
    refresh_expires_delta=86400,
)
# TODO Replace with real db
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "user_id": "ca726425-c408-4246-ac3c-544514f197c3",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "created_at": "22/12/2022 11:00:00",
        "deleted_at": "",
    }
}


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username: str):
    if username in fake_users_db:
        user = fake_users_db[username]
        return user


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


# TODO Implement user registration metod


@router.post("/register")
async def register_user(username: str, password: str):
    hashed_password = pwd_context.hash(password)
    # Сохраните пользователя в базе данных
    return {"username": username, "hashed_password": hashed_password}


# TODO Создать хранилище для токенов (В бд таблицу )
# class UserToken(Base):
#     __tablename__ = "user_tokens"
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     user_id = mapped_column(ForeignKey('users.id'))
#     access_key = Column(String(250), nullable=True, index=True, default=None)
#     refresh_key = Column(String(250), nullable=True, index=True, default=None)
#     created_at = Column(DateTime, nullable=False, server_default=func.now())
#     expires_at = Column(DateTime, nullable=False)
#     user = relationship("User", back_populates="tokens")
@router.post("/token")
async def token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    match form_data.grant_type:
        case "refresh_token":
            # TODO Декодировать рефреш токен
            # TODO сделать запрос в хранилище по access_key и refresh_key
            # TODO проставить дату протухания токена в бд текущей датой
            # TODO создать новый токен, записать его в бд и вернуть его
            # access_security.create_access_token(subject=user.user_id)
            access_security.set_access_cookie(response=response, access_token="подставить токен", expires_delta=900)
            return response
        case "password":
            user = authenticate_user(fake_users_db, form_data.username, form_data.password)
            if not user:
                raise HTTPException(status_code=400, detail="Bad request")
            access_token = access_security.create_access_token(subject="подставить id пользователя")
            refresh_token = access_security.create_refresh_token(subject="подставить id пользователя")
            access_security.set_access_cookie(response=response, access_token=access_token, expires_delta=900)
            access_security.set_refresh_cookie(response=response, refresh_token=refresh_token, expires_delta=86400)
            return response
        case _:
            raise HTTPException(status_code=400, detail="Bad request")
