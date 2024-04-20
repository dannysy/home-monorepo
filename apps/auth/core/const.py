from enum import Enum
from pathlib import Path

PROJECT_DIR = Path(__file__).parent


class AppType(Enum):
    customer = 0
    worker = 1


class TableNames(Enum):
    application: str = 'application'
    login: str = 'login'
    user: str = 'user'
    app_user: str = 'application_user'

    @property
    def value(self):
        return self._value_

    @property
    def hist_value(self):
        return 'history__' + self._value_
