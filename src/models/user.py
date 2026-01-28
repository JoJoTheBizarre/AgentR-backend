from sqlmodel import Field, SQLModel
from uuid import UUID


class User(SQLModel, table=True):
    id: UUID = Field(description="user id", default=None, primary_key=True)
    username: str = Field(description="username for the user", index=True)
    password_hash: str = Field(description="hashed password", default=None)
