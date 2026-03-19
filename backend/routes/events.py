from database import cursor, conn
from fastapi import APIRouter
from psycopg2.extras import Json
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

router = APIRouter()

class Event(BaseModel):
    user_id: int
    event_type: str
    properties: Optional[Dict] = {}
    session_id: str
    timestamp: datetime

@router.post("/events")
def create_event(event: Event):
    cursor.execute(
        """
        INSERT INTO events (user_id, event_type, properties, session_id, timestamp)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            event.user_id,
            event.event_type,
            Json(event.properties),
            event.session_id,
            event.timestamp
        )
    )
    if(event.event_type=="kyc_completed"):
        cursor.execute(
            """
        update users set activated_at=%s where user_id=%s
        """,(event.timestamp,event.user_id)
    )
    elif(event.event_type=="deposit_completed"):
        cursor.execute(
            """
        update users set first_deposit_at=%s where user_id=%s
        """,(event.timestamp,event.user_id)
    )

    conn.commit()
    return {"message": "event stored"}