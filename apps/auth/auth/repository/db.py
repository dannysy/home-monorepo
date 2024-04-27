from uuid import uuid4
from sqlalchemy import create_engine, Column, DateTime, String, UUID
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql.functions import now
from auth import config as app_config

engine = create_engine(app_config.Config.AUTH_POSTGRES_URI)

Session = sessionmaker(bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(UUID, primary_key=True, default=uuid4)
    fio = Column(String(255))
    hashed_password = Column(String(255))
    email = Column(String(255), unique=True)
    phone = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=now(), nullable=False)
    updated_at = Column(DateTime, server_default=now(), onupdate=now(), nullable=False)
    deleted_at = Column(DateTime)
