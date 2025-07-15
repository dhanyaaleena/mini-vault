from fastapi import Request
from fastapi.responses import JSONResponse
from .exceptions import *


def register_error_handlers(app):
    @app.exception_handler(InvalidSession)
    async def invalid_session_handler(request: Request, exc: InvalidSession):
        return JSONResponse(status_code=401, content={"message": str(exc)})

    @app.exception_handler(InvalidCode)
    async def unicorn_exception_handler(request: Request, exc: InvalidCode):
        return JSONResponse(
            status_code=400,
            content={"message": f"Invalid OTP passed"},
        )


    @app.exception_handler(UserNotFound)
    async def unicorn_exception_handler(request: Request, exc: InvalidCode):
        return JSONResponse(
            status_code=404,
            content={"message": f"User not found"},
        )

    @app.exception_handler(InvalidSession)
    async def unicorn_exception_handler(request: Request, exc: InvalidCode):
        return JSONResponse(
            status_code=404,
            content={"message": f"Invalid session passed"},
        )

    @app.exception_handler(FilePermissionError)
    async def unicorn_exception_handler(request: Request, exc: InvalidCode):
        return JSONResponse(
            status_code=403,
            content={"message": f"Permission Denied"},
        )

    @app.exception_handler(FileNotFound)
    async def unicorn_exception_handler(request: Request, exc: InvalidCode):
        return JSONResponse(
            status_code=403,
            content={"message": f"Permission Denied"},
        )