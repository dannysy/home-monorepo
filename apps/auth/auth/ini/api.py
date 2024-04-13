from typing import Iterable
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter, FastAPI

__all__ = ("create",)


def create(
    *_,
    rest_routers: Iterable[APIRouter],
    **kwargs,
) -> FastAPI:

    app = FastAPI(**kwargs)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["POST,GET"],
        allow_headers=["*"],
    )
    for router in rest_routers:
        app.include_router(router)

    # TODO Exception handlers
    #  app.exception_handler(RequestValidationError)(
    #     pydantic_validation_errors_handler
    # )
    # app.exception_handler(ValidationError)(pydantic_validation_errors_handler)
    # app.exception_handler(Exception)(python_base_error_handler)
    return app