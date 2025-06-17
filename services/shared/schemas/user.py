
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    username: str
    is_active: bool | None = True
    role: str | None = "user"
    full_name: str | None = None


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    password: str | None = None


class UserInDBBase(UserBase):
    id: int

    class Config:
        from_attributes = True


# Properties to return to client
class UserInDB(UserInDBBase):
    pass
