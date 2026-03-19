from database import cursor,conn
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router=APIRouter()

class User(BaseModel):
    device_type: Optional[str]="mobile"
    country:Optional[str]="IN"
    signup_at:datetime

@router.post("/users")
def create_user(user: User):
    cursor.execute(
        """
        INSERT INTO users (device_type, country, signup_at)
        VALUES (%s, %s, %s)
        RETURNING user_id
        """,
        (user.device_type, user.country, user.signup_at)
    )

    user_id = cursor.fetchone()[0]
    conn.commit()

    return {"user_id": user_id}

