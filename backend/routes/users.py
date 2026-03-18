from database import cursor,conn
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router=APIRouter()

class Event(BaseModel):
    user_id:int
    device_type: Optional[str]="mobile"
    country:Optional[str]="IN"

@router.post("/users")
def create_event(event:Event):
    cursor.execute(
        """
        insert into events(device_type,country)
        values(%s, %s)
        """,(user.device_type, user.country )

    )
    user_id = cursor.fetchone()[0]
    conn.commit()

    return {"user_id": user_id}
