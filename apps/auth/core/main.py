from fastapi import FastAPI, HTTPException, Request
from starlette.responses import JSONResponse

from .config import Config
from .units.application.router import router as app_router

from .ini import api
from .units.controller import auth, health

# TODO Adjust logging
# -------------------------------
# logger.add(
#     "".join(
#         [
#             str(settings.root_dir),
#             "/logs/",
#             settings.logging.file.lower(),
#             ".log",
#         ]
#     ),
#     format=settings.logging.format,
#     rotation=settings.logging.rotation,
#     compression=settings.logging.compression,
#     level="INFO",
# )


# Adjust the application
# -------------------------------
# app: FastAPI = api.create(
#     debug=Config.AUTH_IS_DEBUG,
#     rest_routers=(auth.router, health.router, app_router),
# )
app = FastAPI()
for router in (auth.router, health.router, app_router):
    app.include_router(router)


@app.get('/')
async def root():
    return {'kek': 1}


@app.exception_handler(HTTPException)
async def base_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )
