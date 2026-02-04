from dataclasses import dataclass
from typing import Generic, TypeVar
from enum import StrEnum

T = TypeVar("T")


class InternalStatus(StrEnum):
    SUCCESS = "success"
    USER_NOT_FOUND = "user_not_found_in_db"
    USER_ALREADY_EXISTS = "user_already_exists"
    DB_CONNECTION_FAILED = "db_connection_failed"
    WRONG_PASSWORD = "wrong_password"
    INVALID_TOKEN = "invalid_token"
    TOKEN_EXPIRED = "token_expired"


@dataclass
class Result(Generic[T]):
    """
    A result type that represents either success with data or failure with status.
    """

    status: InternalStatus
    data: T | None = None
    message: str | None = None

    @property
    def is_success(self) -> bool:
        return self.status == InternalStatus.SUCCESS

    @property
    def is_failure(self) -> bool:
        return not self.is_success

    @classmethod
    def success(cls, data: T | None = None, message: str | None = None) -> "Result[T]":
        return cls(status=InternalStatus.SUCCESS, data=data, message=message)

    @classmethod
    def failure(cls, status: InternalStatus, message: str | None = None) -> "Result[T]":
        return cls(status=status, data=None, message=message)
