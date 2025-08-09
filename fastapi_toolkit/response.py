"""Response helpers for consistent API responses."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel


class BaseResponse(BaseModel):
    """Base response model for all API responses."""
    
    success: bool
    message: str
    timestamp: datetime
    data: Optional[Any] = None
    errors: Optional[List[str]] = None
    meta: Optional[Dict[str, Any]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def __init__(self, **data):
        if 'timestamp' not in data:
            data['timestamp'] = datetime.utcnow()
        super().__init__(**data)


class SuccessResponse(BaseResponse):
    """Success response model."""
    
    def __init__(
        self,
        data: Any = None,
        message: str = "Success",
        meta: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(
            success=True,
            message=message,
            data=data,
            meta=meta,
            **kwargs
        )


class ErrorResponse(BaseResponse):
    """Error response model."""
    
    def __init__(
        self,
        message: str = "An error occurred",
        errors: Optional[List[str]] = None,
        data: Any = None,
        meta: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(
            success=False,
            message=message,
            errors=errors or [],
            data=data,
            meta=meta,
            **kwargs
        )


class PaginatedResponse(SuccessResponse):
    """Paginated response model."""
    
    def __init__(
        self,
        data: List[Any],
        page: int = 1,
        per_page: int = 10,
        total: int = 0,
        message: str = "Success",
        **kwargs
    ):
        total_pages = (total + per_page - 1) // per_page if total > 0 else 0
        
        meta = {
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
        
        super().__init__(
            data=data,
            message=message,
            meta=meta,
            **kwargs
        )


class ValidationErrorResponse(ErrorResponse):
    """Validation error response model."""
    
    def __init__(
        self,
        validation_errors: Dict[str, List[str]],
        message: str = "Validation failed",
        **kwargs
    ):
        errors = []
        for field, field_errors in validation_errors.items():
            for error in field_errors:
                errors.append(f"{field}: {error}")
        
        super().__init__(
            message=message,
            errors=errors,
            data={"validation_errors": validation_errors},
            **kwargs
        )


# Response helper functions
def success(
    data: Any = None,
    message: str = "Success",
    meta: Optional[Dict[str, Any]] = None
) -> SuccessResponse:
    """Create a success response."""
    return SuccessResponse(data=data, message=message, meta=meta)


def error(
    message: str = "An error occurred",
    errors: Optional[List[str]] = None,
    data: Any = None,
    meta: Optional[Dict[str, Any]] = None
) -> ErrorResponse:
    """Create an error response."""
    return ErrorResponse(message=message, errors=errors, data=data, meta=meta)


def paginated(
    data: List[Any],
    page: int = 1,
    per_page: int = 10,
    total: int = 0,
    message: str = "Success"
) -> PaginatedResponse:
    """Create a paginated response."""
    return PaginatedResponse(
        data=data,
        page=page,
        per_page=per_page,
        total=total,
        message=message
    )


def validation_error(
    validation_errors: Dict[str, List[str]],
    message: str = "Validation failed"
) -> ValidationErrorResponse:
    """Create a validation error response."""
    return ValidationErrorResponse(
        validation_errors=validation_errors,
        message=message
    )


def not_found(
    message: str = "Resource not found",
    resource: Optional[str] = None
) -> ErrorResponse:
    """Create a not found error response."""
    if resource:
        message = f"{resource} not found"
    return ErrorResponse(message=message)


def unauthorized(
    message: str = "Unauthorized access"
) -> ErrorResponse:
    """Create an unauthorized error response."""
    return ErrorResponse(message=message)


def forbidden(
    message: str = "Access forbidden"
) -> ErrorResponse:
    """Create a forbidden error response."""
    return ErrorResponse(message=message)


def bad_request(
    message: str = "Bad request",
    errors: Optional[List[str]] = None
) -> ErrorResponse:
    """Create a bad request error response."""
    return ErrorResponse(message=message, errors=errors)


def internal_server_error(
    message: str = "Internal server error",
    error_id: Optional[str] = None
) -> ErrorResponse:
    """Create an internal server error response."""
    meta = {"error_id": error_id} if error_id else None
    return ErrorResponse(message=message, meta=meta)


# HTTP status code mappings
HTTP_STATUS_CODES = {
    "success": 200,
    "created": 201,
    "accepted": 202,
    "no_content": 204,
    "bad_request": 400,
    "unauthorized": 401,
    "forbidden": 403,
    "not_found": 404,
    "method_not_allowed": 405,
    "conflict": 409,
    "unprocessable_entity": 422,
    "internal_server_error": 500,
    "bad_gateway": 502,
    "service_unavailable": 503,
}


def get_status_code(response_type: str) -> int:
    """Get HTTP status code for response type."""
    return HTTP_STATUS_CODES.get(response_type, 200)