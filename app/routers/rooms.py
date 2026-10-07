from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Room
from app.schemas import RoomCreate, RoomRead, RoomUpdate
from app.dependencies import require_admin

router = APIRouter(prefix="/rooms", tags=["rooms"])


def get_room_or_404(room_id: int, db: Session) -> Room:
    room = db.get(Room, room_id)
    if room is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Room not found")
    return room


@router.post("", response_model=RoomRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def create_room(data: RoomCreate, db: Session = Depends(get_db)):
    room = Room(**data.model_dump())
    db.add(room)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Room with this name already exists")
    db.refresh(room)
    return room


@router.get("", response_model=list[RoomRead])
def list_rooms(db: Session = Depends(get_db)):
    query = select(Room).where(Room.is_active.is_(True)).order_by(Room.id)
    return db.scalars(query).all()


@router.get("/{room_id}", response_model=RoomRead)
def get_room(room_id: int, db: Session = Depends(get_db)):
    return get_room_or_404(room_id, db)


@router.patch("/{room_id}", response_model=RoomRead, dependencies=[Depends(require_admin)])
def update_room(room_id: int, data: RoomUpdate, db: Session = Depends(get_db)):
    room = get_room_or_404(room_id, db)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(room, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Room with this name already exists")
    db.refresh(room)
    return room


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def deactivate_room(room_id: int, db: Session = Depends(get_db)):
    room = get_room_or_404(room_id, db)
    room.is_active = False
    db.commit()