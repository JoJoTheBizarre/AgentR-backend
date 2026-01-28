from models import User

def create_user(username: str, password_hash: str) -> User:
    """Create a new user in the database."""
    pass


def get_user_by_id(user_id: str) -> User:
    """Retrieve a user by their ID."""
    pass


def get_user_by_username(username: str) -> User | None:
    """Retrieve a user by their username raises error if does not exist."""
    pass


def update_user(user_id: str, **kwargs) -> User:
    """Update user fields."""
    pass


def delete_user(user_id: str) -> bool:
    """Delete a user. Returns True if successful."""
    pass


def user_exists(username: str) -> bool:
    """Check if a username already exists."""
    pass


def update_password(user_id: str, new_password_hash: str) -> bool:
    """Update a user's password hash. Returns True if successful."""
    pass


def get_all_users() -> list[User]:
    """Retrieve all users."""
    pass