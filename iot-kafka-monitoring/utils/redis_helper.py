import redis
import json
from config.settings import settings

class RedisHelper:
    """
    Classe utilitária para operações de deduplicação e cache em Redis.
    Usa configurações centralizadas do settings, mas permite sobrescrever para testes.
    """
    def __init__(self, host=None, port=None, ttl=None):
        self.client = redis.Redis(
            host=host or settings.REDIS_HOST,
            port=port or settings.REDIS_PORT,
            decode_responses=True
        )
        self.ttl = ttl or settings.REDIS_TTL_SECONDS

    def is_duplicate(self, reading_id):
        return self.client.exists(f"reading:{reading_id}")

    def mark_as_processed(self, reading_id):
        self.client.setex(f"reading:{reading_id}", self.ttl, 1)

    def cache_last_value(self, sensor_id, data):
        self.client.set(f"last:{sensor_id}", json.dumps(data))

    def get_last_value(self, sensor_id):
        return self.client.get(f"last:{sensor_id}")