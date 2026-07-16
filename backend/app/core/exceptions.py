"""Shared application exceptions."""


class ApplicationError(Exception):
    """Base exception carrying a safe API error representation."""

    code = "APPLICATION_ERROR"
    default_message = "An application error occurred."
    status_code = 500

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.default_message
        super().__init__(self.message)


class ValidationError(ApplicationError):
    """Raised when input validation fails."""
    code, default_message, status_code = "VALIDATION_ERROR", "Validation failed.", 400


class AuthenticationError(ApplicationError):
    """Raised when authentication fails."""
    code = "AUTHENTICATION_ERROR"
    default_message = "Authentication failed."
    status_code = 401


class AuthorizationError(ApplicationError):
    """Raised when access is not permitted."""
    code = "AUTHORIZATION_ERROR"
    default_message = "Access is not permitted."
    status_code = 403


class NotFoundError(ApplicationError):
    """Raised when requested data does not exist."""
    code = "NOT_FOUND_ERROR"
    default_message = "The requested resource was not found."
    status_code = 404


class BusinessRuleError(ApplicationError):
    """Raised when a business rule is violated."""
    code = "BUSINESS_RULE_ERROR"
    default_message = "A business rule was violated."
    status_code = 409


class AIServiceError(ApplicationError):
    """Raised when AI processing fails."""
    code, default_message, status_code = "AI_SERVICE_ERROR", "The AI service failed.", 500


class StorageError(ApplicationError):
    """Raised when storage processing fails."""
    code = "STORAGE_ERROR"
    default_message = "The storage operation failed."
    status_code = 500
