import redis
from auth import config as app_config

_pool = redis.ConnectionPool(
    host=app_config.Config.AUTH_REDIS_HOST, port=app_config.Config.AUTH_REDIS_PORT, decode_responses=True
)
gist = redis.Redis(connection_pool=_pool)
