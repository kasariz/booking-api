from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.routers import rooms
from app.database import get_db
from app.routers import auth, rooms

app = FastAPI(title="Booking API")
app.include_router(auth.router)
app.include_router(rooms.router)

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "ok"}