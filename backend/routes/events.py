from database import cursor,conn
from fastapi import APIRouter
from psycopg2.extras import Json
from pydantic import BaseModel
from typing import Optional,Dict

router=APIRouter()

class Event(BaseModel):
    user_id:int
    event_name: str
    properties:Optional[Dict]={}

@router.post("/events")
def create_event(event:Event):
    cursor.execute(
        """
        insert into events(user_id,event_name,properties)
        values(%s, %s, %s)
        """,(event.user_id,event.event_name,Json(event.properties) )

    )
    conn.commit()
    return {"message":"event stored"}
