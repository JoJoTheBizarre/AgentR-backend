from sqlmodel import Field, SQLModel
from uuid import UUID
from datetime import datetime


class User(SQLModel, table=True):
    id: UUID = Field(..., description="user id", primary_key=True)
    username: str = Field(..., description="username for the user", index=True)
    password_hash: str = Field(..., description="hashed password")
    created_at: datetime = Field(..., description="timestamp when the user was created")
    updated_at: datetime = Field(
        ..., description="timestamp when the user was last updated"
    )
