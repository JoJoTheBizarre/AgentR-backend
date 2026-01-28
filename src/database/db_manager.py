from contextlib import contextmanager
from typing import Generator
from sqlmodel import Session, create_engine


class DatabaseManager:
    """Database manager that provides a context manager for database sessions."""
    
    def __init__(self, database_url: str, echo: bool = False, **engine_kwargs):
        self.engine = create_engine(database_url, echo=echo, **engine_kwargs)
    
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