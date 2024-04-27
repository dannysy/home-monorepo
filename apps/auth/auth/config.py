import os
from typing import get_type_hints, Union
from dotenv import load_dotenv  # type: ignore

load_dotenv()


class AppConfigError(Exception):
    pass


def _parse_bool(val: Union[str, bool]) -> bool:
    return val if type(val) == bool else val.lower() in ["true", "yes", "1"]  # noqa: E721


class AppConfig:
    AUTH_IS_DEBUG: bool
    AUTH_JWT_SECRET: str
    AUTH_POSTGRES_URI: str
    AUTH_REDIS_HOST: str
    AUTH_REDIS_PORT: int
    AUTH_WHATSUP_INSTANCE_ID: str
    AUTH_WHATSUP_INSTANCE_TOKEN: str

    def __init__(self, env):
        for field in self.__annotations__:
            if not field.isupper():
                continue

            default_value = getattr(self, field, None)
            if default_value is None and env.get(field) is None:
                raise AppConfigError("The {} field is required".format(field))

            try:
                var_type = get_type_hints(AppConfig)[field]
                if var_type == bool:
                    value = _parse_bool(env.get(field, default_value))
                else:
                    value = var_type(env.get(field, default_value))

                self.__setattr__(field, value)
            except ValueError:
                raise AppConfigError(
                    'Unable to cast value of "{}" to type "{}" for "{}" field'.format(env[field], var_type, field)
                )

    def __repr__(self):
        return str(self.__dict__)


# Create an instance of AppConfig
Config = AppConfig(os.environ)
