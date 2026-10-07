from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Booking, Room, User, UserRole
from app.schemas import BookingCreate, BookingRead

router = APIRouter(tags=["bookings"])


@router.post("/bookings", response_model=BookingRead, status_code=status.HTTP_201_CREATED)
def create_booking(
    data: BookingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    room = db.get(Room, data.room_id, with_for_update=True)
    if room is None or not room.is_active:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Room not found")

    overlapping = db.scalar(
        select(Booking.id)
        .where(
            Booking.room_id == data.room_id,
            Booking.start_time < data.end_time,
            Booking.end_time > data.start_time,
        )
        .limit(1)
    )
    if overlapping is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Room is already booked for this time")

    booking = Booking(**data.model_dump(), user_id=user.id)
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@router.get("/bookings/me", response_model=list[BookingRead])
def list_my_bookings(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = select(Booking).where(Booking.user_id == user.id).order_by(Booking.start_time)
    return db.scalars(query).all()


@router.get(
    "/rooms/{room_id}/bookings",
    response_model=list[BookingRead],
    dependencies=[Depends(get_current_user)],
)
def list_room_bookings(room_id: int, db: Session = Depends(get_db)):
    if db.get(Room, room_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Room not found")
    query = (
        select(Booking)
        .where(Booking.room_id == room_id, Booking.end_time > datetime.now(UTC))
        .order_by(Booking.start_time)
    )
    return db.scalars(query).all()


@router.delete("/bookings/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    booking = db.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Booking not found")
    if booking.user_id != user.id and user.role != UserRole.ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="You can cancel only your own bookings")
    db.delete(booking)
    db.commit()