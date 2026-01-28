from enum import StrEnum

class StatusDetail(StrEnum):
    INVALID_CREDENTIALS = "Invalid username or password"
    USERNAME_ALREAY_EXISTS = "username already exists"
    SUCCESS = "Success"