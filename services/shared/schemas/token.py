
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str | None = None


class TokenPayload(BaseModel):
    sub: str | None = None
    exp: int | None = None
    user_id: int | None = None
    roles: list[str] | None = None
    type: str | None = None
    jti: str | None = None
