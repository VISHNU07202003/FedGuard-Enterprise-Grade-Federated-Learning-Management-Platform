from fastapi import Request, status
from fastapi.responses import JSONResponse

class FedGuardError(Exception):
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)

class NotFoundError(FedGuardError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, code="NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)

class ValidationError(FedGuardError):
    def __init__(self, message: str = "Validation error"):
        super().__init__(message, code="VALIDATION_ERROR", status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

class AuthenticationError(FedGuardError):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, code="AUTHENTICATION_ERROR", status_code=status.HTTP_401_UNAUTHORIZED)

class AuthorizationError(FedGuardError):
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, code="AUTHORIZATION_ERROR", status_code=status.HTTP_403_FORBIDDEN)

async def fedguard_exception_handler(request: Request, exc: FedGuardError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message}},
    )
