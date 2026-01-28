from pydantic import BaseModel, Field
from datetime import datetime


class User(BaseModel):
    username: str = Field(..., max_length=50)
    id: str
    password_hash: str
    created_at: datetime
    updated_at: datetime