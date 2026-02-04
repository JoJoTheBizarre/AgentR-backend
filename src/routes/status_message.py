class StatusMessage:
    """User-facing status messages for API responses."""

    # Success
    SUCCESS = "success"
    OPERATION_SUCCESSFUL = "Operation completed successfully"

    # Authentication
    INVALID_CREDENTIALS = "Invalid username or password"
    UNAUTHORIZED = "Authentication required"
    TOKEN_EXPIRED = "Your session has expired. Please login again"
    INVALID_TOKEN = "Invalid authentication token"
    AUTHENTICATION_FAILED = "Authentication failed"

    # Registration
    REGISTRATION_SUCCESSFUL = "Account created successfully"
    USERNAME_TAKEN = "This username is already taken"

    # User management
    USER_NOT_FOUND = "User not found"
    PROFILE_UPDATED = "Profile updated successfully"
    ACCOUNT_DELETED = "Account deleted successfully"

    # Password
    PASSWORD_CHANGED = "Password changed successfully"
    PASSWORD_RESET = "Password reset successfully"
    WRONG_PASSWORD = "Current password is incorrect"
    PASSWORD_TOO_WEAK = "Password must be at least 8 characters"

    # Server errors
    INTERNAL_ERROR = "An unexpected error occurred. Please try again later"
    SERVICE_UNAVAILABLE = "Service is temporarily unavailable"
    DATABASE_ERROR = "Database operation failed"

    # Validation
    INVALID_INPUT = "The provided input is invalid"
    MISSING_REQUIRED_FIELDS = "Required fields are missing"
