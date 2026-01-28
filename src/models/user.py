from datetime import datetime

from pydantic import BaseModel, Field


class User(BaseModel):
    username: str = Field(..., max_length=50)
    id: str
    password_hash: str
    created_at: datetime
    updated_at: datetime