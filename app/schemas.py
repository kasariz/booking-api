from datetime import UTC, datetime, timedelta

from pydantic import AwareDatetime, BaseModel, ConfigDict, EmailStr, Field, model_validator

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

MAX_BOOKING_DURATION = timedelta(hours=8)


class BookingCreate(BaseModel):
    room_id: int
    start_time: AwareDatetime
    end_time: AwareDatetime

    @model_validator(mode="after")
    def check_time_range(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        if self.start_time < datetime.now(UTC):
            raise ValueError("start_time must be in the future")
        if self.end_time - self.start_time > MAX_BOOKING_DURATION:
            raise ValueError("Booking cannot be longer than 8 hours")
        return self


class BookingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    room_id: int
    user_id: int
    start_time: datetime
    end_time: datetime
    created_at: datetime