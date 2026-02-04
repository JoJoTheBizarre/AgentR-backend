from contextlib import contextmanager
from typing import Generator, Optional
from sqlmodel import Session, create_engine
from sqlalchemy.engine import Engine


class DatabaseManager:
    """Database manager that provides a context manager for database sessions."""

    def __init__(self, database_url: str, echo: bool = False, **engine_kwargs):
        self.engine: Engine = create_engine(
            database_url,
            echo=echo,
            **engine_kwargs,
        )

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        session = Session(self.engine)
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def dispose(self):
        self.engine.dispose()


_db_manager: Optional[DatabaseManager] = None

def init_database(
    database_url: str,
    echo: bool = False,
    **engine_kwargs,
) -> None:
    global _db_manager

    if _db_manager is not None:
        raise RuntimeError("Database already initialized")

    _db_manager = DatabaseManager(database_url, echo, **engine_kwargs)

def get_database() -> DatabaseManager:
    if _db_manager is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return _db_manager

