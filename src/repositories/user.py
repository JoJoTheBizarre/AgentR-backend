from sqlmodel import select

from src.db.models import User
from src.db import DatabaseManager, get_database

class UserRepository:
    """Repository for User database operations."""

    def __init__(self, db_manager: DatabaseManager | None = None):
        if db_manager is None:
            db_manager = get_database()

        self.db_manager = db_manager

    def create(self, user: User) -> User:
        with self.db_manager.session() as session:
            session.add(user)
            session.flush()
            session.refresh(user)
            return user

    def get_by_id(self, user_id: str) -> User | None:
        with self.db_manager.session() as session:
            user = session.get(User, user_id)
            return user

    def get_by_username(self, username: str) -> User | None:
        with self.db_manager.session() as session:
            statement = select(User).where(User.username == username)
            user = session.exec(statement).first()
            return user

    def get_all(self) -> list[User]:
        with self.db_manager.session() as session:
            statement = select(User)
            users = session.exec(statement).all()
            return list(users)

    def exists(self, username: str) -> bool:
        return self.get_by_username(username) is not None

    def update(self, user_id: str, **kwargs) -> User:
        with self.db_manager.session() as session:
            user = session.get(User, user_id)
            if not user:
                raise ValueError(f"User with id {user_id} not found")

            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)

            session.add(user)
            session.flush()
            session.refresh(user)
            return user

    def update_password(self, user_id: str, new_password_hash: str) -> bool:
        with self.db_manager.session() as session:
            user = session.get(User, user_id)
            if not user:
                return False

            user.password_hash = new_password_hash
            session.add(user)
            return True

    def delete(self, user_id: str) -> bool:
        with self.db_manager.session() as session:
            user = session.get(User, user_id)
            if not user:
                return False

            session.delete(user)
            return True
