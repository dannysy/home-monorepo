from typing import Optional

from pydantic import BaseModel, model_validator, ConfigDict

from core.const import AppType
from core.schema import ReceivedBasic


class ReceivedAppReg(BaseModel):
    app_type: AppType
    device_info: str
    app_version: int


class ReceivedAppUpd(ReceivedBasic):
    device_info: Optional[str] = None
    app_version: Optional[int] = None

    @model_validator(mode='after')
    def verify(self) -> 'ReceivedAppUpd':
        if all([self.device_info is None, self.app_version is None]):
            raise ValueError('Both attrs (device_info and app_version) is None')
        return self


class SendAppReg(BaseModel):
    id: int

    model_config = ConfigDict(from_attributes=True)