from pydantic import BaseModel


class TokenRequest(BaseModel):
    grant_type: str
    username: str
    password: str
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: str
    refresh_token: str
    user_id: str
