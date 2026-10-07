from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import UserRole

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=100)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    role: UserRole


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class RoomBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    capacity: int = Field(gt=0, le=1000)
    description: str | None = Field(default=None, max_length=500)


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    capacity: int | None = Field(default=None, gt=0, le=1000)
    description: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None


class RoomRead(RoomBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool