from pydantic_settings import BaseSettings


class AuthSettings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    token_expire_minutes: int

    class Config:
        env_file = ".env"


class DatabaseSettings(BaseSettings):
    DATABASE_URL: str
