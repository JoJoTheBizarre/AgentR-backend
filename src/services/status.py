from enum import StrEnum

class InternalStatus(StrEnum):
    SUCCESS = "success"
    USER_NOT_FOUND = "user_not_found_in_db"
    USER_ALREADY_EXISTS = "user_already_exists"
    DB_CONNECTION_FAILED = "db_connection_failed"
    WRONG_PASSWORD = "wrong password for the given username"