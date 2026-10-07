from pydantic import BaseModel, ConfigDict, Field


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