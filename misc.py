from redis.asyncio import Redis

import config

redis = Redis(
    host=config.redis_host or '127.0.0.1'
)
