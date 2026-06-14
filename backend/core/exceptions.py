from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from core.logging_config import logger

class LLMRateLimitException(Exception):
    def __init__(self, message: str = "Our AI reasoning capacity is currently busy. Please wait a few moments and try again."):
        self.message = message
        super().__init__(self.message)

class ServiceUnavailableException(Exception):
    def __init__(self, message: str = "Our core legal database services are temporarily offline. Please try again shortly."):
        self.message = message
        super().__init__(self.message)

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(LLMRateLimitException)
    async def rate_limit_exception_handler(request: Request, exc: LLMRateLimitException):
        logger.warning(f"Rate limit exception caught at {request.url.path}: {exc.message}")
        return JSONResponse(
            status_code=429,
            content={"detail": exc.message}
        )

    @app.exception_handler(ServiceUnavailableException)
    async def service_unavailable_exception_handler(request: Request, exc: ServiceUnavailableException):
        logger.error(f"Service unavailable exception caught at {request.url.path}: {exc.message}")
        return JSONResponse(
            status_code=503,
            content={"detail": exc.message}
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception occurred at {request.url.path}: {exc}", exc_info=True)
        # Prevent leaking raw python exceptions to user, return clean 500
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred while processing legal logic. Please try again."}
        )
