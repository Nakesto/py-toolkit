"""Middleware components for FastAPI applications."""

import asyncio
import json
import logging
import time
from typing import Callable, Optional, List

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware as FastAPICORSMiddleware
from fastapi.responses import JSONResponse
from starlette.types import ASGIApp


class TimeoutMiddleware(BaseHTTPMiddleware):
    """Middleware to handle request timeouts."""
    
    def __init__(self, app: ASGIApp, timeout_seconds: float = 30.0):
        super().__init__(app)
        self.timeout_seconds = timeout_seconds
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await asyncio.wait_for(
                call_next(request),
                timeout=self.timeout_seconds
            )
        except asyncio.TimeoutError:
            return JSONResponse(
                status_code=408,
                content={
                    "error": "Request timeout",
                    "message": f"Request took longer than {self.timeout_seconds} seconds"
                }
            )


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log requests and responses."""
    
    def __init__(
        self,
        app: ASGIApp,
        logger: Optional[logging.Logger] = None,
        log_request_body: bool = False,
        log_response_body: bool = False
    ):
        super().__init__(app)
        self.logger = logger or logging.getLogger(__name__)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Log request
        request_info = {
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "client_ip": request.client.host if request.client else None
        }
        
        if self.log_request_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    request_info["body"] = body.decode("utf-8")
            except Exception:
                request_info["body"] = "<unable to decode>"
        
        self.logger.info(f"Request: {json.dumps(request_info)}")
        
        # Process request
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        response_info = {
            "status_code": response.status_code,
            "process_time": round(process_time, 4),
            "headers": dict(response.headers)
        }
        
        if self.log_response_body and hasattr(response, 'body'):
            try:
                response_info["body"] = response.body.decode("utf-8")
            except Exception:
                response_info["body"] = "<unable to decode>"
        
        self.logger.info(f"Response: {json.dumps(response_info)}")
        
        return response


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware to handle and format errors consistently."""
    
    def __init__(
        self,
        app: ASGIApp,
        logger: Optional[logging.Logger] = None,
        include_traceback: bool = False
    ):
        super().__init__(app)
        self.logger = logger or logging.getLogger(__name__)
        self.include_traceback = include_traceback
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except Exception as exc:
            import traceback
            
            error_id = f"error_{int(time.time())}_{id(exc)}"
            
            error_info = {
                "error_id": error_id,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "path": request.url.path,
                "method": request.method
            }
            
            if self.include_traceback:
                error_info["traceback"] = traceback.format_exc()
            
            self.logger.error(f"Unhandled error: {json.dumps(error_info)}")
            
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": "An unexpected error occurred",
                    "error_id": error_id
                }
            )


class CORSMiddleware:
    """Wrapper for FastAPI CORS middleware with sensible defaults."""
    
    @staticmethod
    def add_cors(
        app: FastAPI,
        allow_origins: List[str] = ["*"],
        allow_credentials: bool = True,
        allow_methods: List[str] = ["*"],
        allow_headers: List[str] = ["*"]
    ) -> None:
        """Add CORS middleware to FastAPI app."""
        app.add_middleware(
            FastAPICORSMiddleware,
            allow_origins=allow_origins,
            allow_credentials=allow_credentials,
            allow_methods=allow_methods,
            allow_headers=allow_headers
        )


def setup_middleware(
    app: FastAPI,
    timeout_seconds: float = 30.0,
    enable_logging: bool = True,
    enable_error_handler: bool = True,
    enable_cors: bool = True,
    cors_origins: List[str] = ["*"],
    logger: Optional[logging.Logger] = None
) -> None:
    """Setup all middleware with sensible defaults."""
    
    if enable_cors:
        CORSMiddleware.add_cors(app, allow_origins=cors_origins)
    
    if enable_error_handler:
        app.add_middleware(ErrorHandlerMiddleware, logger=logger)
    
    if enable_logging:
        app.add_middleware(LoggingMiddleware, logger=logger)
    
    app.add_middleware(TimeoutMiddleware, timeout_seconds=timeout_seconds)