from pathlib import Path
from functools import lru_cache

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=Path(__file__).parent / '.env', extra='ignore')

    dsn: PostgresDsn
    postgresql_image: str = ""
    authjwt_secret_key: str = "secret"

    @property
    def connection_string(self):
        return str(self.dsn)


# @AuthJWT.load_config
@lru_cache()
def get_config():
    return Settings()



