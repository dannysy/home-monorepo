from typing import NamedTuple
from collections import OrderedDict
from apps.auth.core.const import AppType


class Application(NamedTuple):
    id: int
    app_type: AppType


class APPStatus:
    _limit_exist = 100_000
    _limit_not_exist = 1_000_000
    _load_last_days = 7

    # TODO: необходимо ограничить размеры справочников

    def __init__(self):
        # TODO: При инициализации должен подгружать N активных приложений за последнее время.
        self._reged: OrderedDict[int, None] = OrderedDict()
        self._notreged: OrderedDict[int, None] = OrderedDict()

    def add_reged_app(self, app_id: int) -> None:
        self._reged[app_id] = None
        if len(self._reged) > self._limit_exist:
            self._reged.popitem(last=False)
        self._notreged.pop(app_id, None)

    def add_notreged_app(self, app_id: int) -> None:
        self._notreged[app_id] = None
        if len(self._notreged) > self._limit_not_exist:
            self._notreged.popitem(last=False)
        self._reged.pop(app_id, None)

    def is_reged_app(self, app_id: int, move_to_end: bool = False) -> bool | None:
        if app_id in self._reged:
            if move_to_end:
                self._reged.move_to_end(app_id)
            return True
        elif app_id in self._notreged:
            if move_to_end:
                self._notreged.move_to_end(app_id)
            return False


app_status = APPStatus()


def is_reged_app(app_id: int, move_to_end: bool = True) -> bool | None:
    return app_status.is_reged_app(app_id, move_to_end)


def add_notreged_app(app_id: int) -> None:
    app_status.add_notreged_app(app_id)


def add_reged_app(app_id: int) -> None:
    app_status.add_reged_app(app_id)
