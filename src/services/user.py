from datetime import datetime, timezone
from typing import Optional
import uuid
from passlib.context import CryptContext

from src.repositories.user import UserRepository
from src.db.models import User
from src.services.status import InternalStatus, Result


class UserService:
    """Handles user registration and management operations."""

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def __init__(self, user_repository: UserRepository | None = None):
        """
        Initialize UserService.
        
        Args:
            user_repository: Optional UserRepository instance for dependency injection
        """
        self.user_repository = user_repository or UserRepository()

    def register_user(self, username: str, plain_password: str) -> Result[User]:
        """Register a new user with the given credentials."""
        if self.user_repository.exists(username):
            return Result.failure(
                InternalStatus.USER_ALREADY_EXISTS,
                f"Username '{username}' is already taken"
            )

        user = User(
            id=uuid.uuid4(),
            username=username,
            password_hash=self.pwd_context.hash(plain_password),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        created_user = self.user_repository.create(user)
        return Result.success(created_user, "User registered successfully")

    def get_user_by_id(self, user_id: str) -> Result[User]:
        """Retrieve a user by their ID."""
        user = self.user_repository.get_by_id(user_id)
        
        if not user:
            return Result.failure(
                InternalStatus.USER_NOT_FOUND,
                f"User with ID '{user_id}' not found"
            )
        
        return Result.success(user)

    def get_user_by_username(self, username: str) -> Result[User]:
        """Retrieve a user by their username."""
        user = self.user_repository.get_by_username(username)
        
        if not user:
            return Result.failure(
                InternalStatus.USER_NOT_FOUND,
                f"User '{username}' not found"
            )
        
        return Result.success(user)

    def get_all_users(self) -> Result[list[User]]:
        """Retrieve all users from the database."""
        users = self.user_repository.get_all()
        return Result.success(users, f"Retrieved {len(users)} users")

    def user_exists(self, username: str) -> bool:
        """Check if a user with the given username exists."""
        return self.user_repository.exists(username)

    def update_user(
        self, user_id: str, username: Optional[str] = None, **kwargs
    ) -> Result[User]:
        """Update user information."""
        try:
            # Check if user exists
            existing_user = self.user_repository.get_by_id(user_id)
            if not existing_user:
                return Result.failure(
                    InternalStatus.USER_NOT_FOUND,
                    f"User with ID '{user_id}' not found"
                )

            # If updating username, check if new username is already taken
            if username and username != existing_user.username:
                if self.user_repository.exists(username):
                    return Result.failure(
                        InternalStatus.USER_ALREADY_EXISTS,
                        f"Username '{username}' is already taken"
                    )
                kwargs["username"] = username

            # Add updated_at timestamp
            kwargs["updated_at"] = datetime.now(timezone.utc)

            updated_user = self.user_repository.update(user_id, **kwargs)
            return Result.success(updated_user, "User updated successfully")

        except ValueError:
            return Result.failure(
                InternalStatus.USER_NOT_FOUND,
                f"User with ID '{user_id}' not found"
            )

    def change_password(
        self, user_id: str, old_password: str, new_password: str
    ) -> Result[None]:
        """Change a user's password after verifying the old password."""
        user = self.user_repository.get_by_id(user_id)
        
        if not user:
            return Result.failure(
                InternalStatus.USER_NOT_FOUND,
                f"User with ID '{user_id}' not found"
            )

        # Verify old password
        if not self.pwd_context.verify(old_password, user.password_hash):
            return Result.failure(
                InternalStatus.WRONG_PASSWORD,
                "Current password is incorrect"
            )

        # Hash and update new password
        new_password_hash = self.pwd_context.hash(new_password)
        success = self.user_repository.update_password(user_id, new_password_hash)

        if not success:
            return Result.failure(
                InternalStatus.USER_NOT_FOUND,
                f"Failed to update password for user '{user_id}'"
            )
        
        return Result.success(message="Password changed successfully")

    def reset_password(self, user_id: str, new_password: str) -> Result[None]:
        """Reset a user's password without requiring the old password."""
        if not self.user_repository.get_by_id(user_id):
            return Result.failure(
                InternalStatus.USER_NOT_FOUND,
                f"User with ID '{user_id}' not found"
            )

        new_password_hash = self.pwd_context.hash(new_password)
        success = self.user_repository.update_password(user_id, new_password_hash)

        if not success:
            return Result.failure(
                InternalStatus.USER_NOT_FOUND,
                f"Failed to reset password for user '{user_id}'"
            )
        
        return Result.success(message="Password reset successfully")

    def delete_user(self, user_id: str) -> Result[None]:
        """Delete a user from the database."""
        success = self.user_repository.delete(user_id)
        
        if not success:
            return Result.failure(
                InternalStatus.USER_NOT_FOUND,
                f"User with ID '{user_id}' not found"
            )
        
        return Result.success(message="User deleted successfully")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain text password against a hashed password."""
        return self.pwd_context.verify(plain_password, hashed_password)

    def hash_password(self, plain_password: str) -> str:
        """Hash a plain text password."""
        return self.pwd_context.hash(plain_password)