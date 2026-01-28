from enum import StrEnum


class StatusDetail(StrEnum):
    INVALID_CREDENTIALS = "Invalid username or password"
    USER_ALREADY_EXISTS = "username already exists"
    SUCCESS = "Success"
