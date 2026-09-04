from fastapi import Request
from fastapi.responses import JSONResponse


class WorkbenchException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AirGappedSecurityViolation(WorkbenchException):
    def __init__(self, message: str = "Outbound network request prohibited in air-gapped sovereign mode."):
        super().__init__(message, status_code=403)


class ModelAvailabilityError(WorkbenchException):
    def __init__(self, message: str = "Requested local model is unavailable."):
        super().__init__(message, status_code=503)


class ModelIntegrityError(WorkbenchException):
    def __init__(self, message: str = "Model artifact integrity verification failed."):
        super().__init__(message, status_code=500)


class RBACPermissionDenied(WorkbenchException):
    def __init__(self, message: str = "Permission denied: insufficient role privileges."):
        super().__init__(message, status_code=403)


class AuthenticationRequired(WorkbenchException):
    def __init__(self, message: str = "Authentication required."):
        super().__init__(message, status_code=401)


class SecurityValidationError(WorkbenchException):
    def __init__(self, message: str = "Security validation failed."):
        super().__init__(message, status_code=400)


async def workbench_exception_handler(
    request: Request,
    exc: WorkbenchException,
) -> JSONResponse:
    from app.core.security import redact_sensitive_text

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": redact_sensitive_text(exc.message),
        },
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
        },
    )
