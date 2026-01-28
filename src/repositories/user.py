from sqlmodel import select

from src.models import User
from src.database import DatabaseManager
from src.settings import DatabaseSettings


database_config = DatabaseSettings()  # type: ignore
db_manager = DatabaseManager(database_config.DATABASE_URL)


def create_user(user: User) -> User:
    """Create a new user in the database."""
    with db_manager.session() as session:
        session.add(user)
        session.flush()  # Get the ID immediately
        session.refresh(user)
        return user


def get_user_by_id(user_id: str) -> User:
    """Retrieve a user by their ID."""
    with db_manager.session() as session:
        user = session.get(User, user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")
        return user


def get_user_by_username(username: str) -> User | None:
    """Retrieve a user by their username, returns None if not found."""
    with db_manager.session() as session:
        statement = select(User).where(User.username == username)
        user = session.exec(statement).first()
        return user


def update_user(user_id: str, **kwargs) -> User:
    """Update user fields."""
    with db_manager.session() as session:
        user = session.get(User, user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")
        
        # Update only provided fields
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        session.add(user)
        session.flush()
        session.refresh(user)
        return user


def delete_user(user_id: str) -> bool:
    """Delete a user. Returns True if successful."""
    with db_manager.session() as session:
        user = session.get(User, user_id)
        if not user:
            return False
        
        session.delete(user)
        return True


def user_exists(username: str) -> bool:
    """Check if a username already exists."""
    with db_manager.session() as session:
        statement = select(User).where(User.username == username)
        user = session.exec(statement).first()
        return user is not None


def update_password(user_id: str, new_password_hash: str) -> bool:
    """Update a user's password hash. Returns True if successful."""
    with db_manager.session() as session:
        user = session.get(User, user_id)
        if not user:
            return False
        
        user.password_hash = new_password_hash
        session.add(user)
        return True


def get_all_users() -> list[User]:
    """Retrieve all users."""
    with db_manager.session() as session:
        statement = select(User)
        users = session.exec(statement).all()
        return list(users)