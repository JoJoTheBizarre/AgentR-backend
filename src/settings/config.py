from pydantic_settings import BaseSettings


class AuthSettings(BaseSettings):
    SECRET_KEY: str = "dev-secret-key-change-in-production"  # Default for development
    ALGORITHM: str = "HS256"
    token_expire_minutes: int = 30  # Default 30 minutes

    class Config:
        env_file = ".env"

class DatabaseSettings(BaseSettings):
    DATABASE_URL: str