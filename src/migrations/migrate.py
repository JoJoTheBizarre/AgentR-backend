from src.models import *  # noqa: F403
from src.settings import DatabaseSettings
from sqlmodel import create_engine, SQLModel


if __name__ == "__main__":
    db_settings = DatabaseSettings()  # type: ignore
    engine = create_engine(db_settings.DATABASE_URL, echo=True)
    SQLModel.metadata.create_all(engine)
