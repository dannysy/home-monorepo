from fastapi import FastAPI
# from loguru import logger

from .config import Config
from .ini import api
from .controller import auth, health

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
app: FastAPI = api.create(
    debug=Config.AUTH_IS_DEBUG,
    rest_routers=(auth.router, health.router),
)
