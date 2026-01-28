from pydantic_settings import BaseSettings

class AuthSettings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    expire: int

    class Config:
        env_file = ".env"