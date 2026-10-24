"""
Custom application exceptions with HTTP status codes and error codes.
"""


class AppException(Exception):
    """Base application exception."""

    status_code: int = 400
    error_code: str = "APP_ERROR"

    def __init__(self, message: str = "An error occurred", error_code: str = None):
        self.message = message
        if error_code:
            self.error_code = error_code
        super().__init__(self.message)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.message!r})"


class UserAlreadyExistsError(AppException):
    status_code = 409
    error_code = "USER_ALREADY_EXISTS"

    def __init__(self, message: str = "A user with this email already exists."):
        super().__init__(message)


class InvalidCredentialsError(AppException):
    status_code = 401
    error_code = "INVALID_CREDENTIALS"

    def __init__(self, message: str = "Invalid email or password."):
        super().__init__(message)


class UserNotFoundError(AppException):
    status_code = 404
    error_code = "USER_NOT_FOUND"

    def __init__(self, message: str = "User not found."):
        super().__init__(message)


class UnauthorizedError(AppException):
    status_code = 403
    error_code = "UNAUTHORIZED"

    def __init__(self, message: str = "You do not have permission to perform this action."):
        super().__init__(message)


class JobNotFoundError(AppException):
    status_code = 404
    error_code = "JOB_NOT_FOUND"

    def __init__(self, message: str = "Job not found."):
        super().__init__(message)


class JobClosedError(AppException):
    status_code = 400
    error_code = "JOB_CLOSED"

    def __init__(self, message: str = "This job is no longer accepting applications."):
        super().__init__(message)


class DuplicateApplicationError(AppException):
    status_code = 409
    error_code = "DUPLICATE_APPLICATION"

    def __init__(self, message: str = "You have already applied for this job."):
        super().__init__(message)


class ApplicationNotFoundError(AppException):
    status_code = 404
    error_code = "APPLICATION_NOT_FOUND"

    def __init__(self, message: str = "Application not found."):
        super().__init__(message)


class InvalidApplicationStatusError(AppException):
    status_code = 400
    error_code = "INVALID_APPLICATION_STATUS"

    def __init__(self, message: str = "Invalid application status transition."):
        super().__init__(message)


class ResumeUploadError(AppException):
    status_code = 400
    error_code = "RESUME_UPLOAD_ERROR"

    def __init__(self, message: str = "Resume upload failed."):
        super().__init__(message)


class ValidationError(AppException):
    status_code = 422
    error_code = "VALIDATION_ERROR"

    def __init__(self, message: str = "Validation failed.", field: str = None):
        self.field = field
        super().__init__(message)


class CompanyNotFoundError(AppException):
    status_code = 404
    error_code = "COMPANY_NOT_FOUND"

    def __init__(self, message: str = "Company not found."):
        super().__init__(message)


class InterviewNotFoundError(AppException):
    status_code = 404
    error_code = "INTERVIEW_NOT_FOUND"

    def __init__(self, message: str = "Interview not found."):
        super().__init__(message)
