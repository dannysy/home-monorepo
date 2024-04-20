from pydantic import BaseModel


class ReceivedBasic(BaseModel):
    sender_app_id: int
