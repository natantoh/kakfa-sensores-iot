import redis
import json
import os

REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
REDIS_TTL_SECONDS = 3600

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def is_duplicate(reading_id):
    return redis_client.exists(f"reading:{reading_id}")

def mark_as_processed(reading_id):
    redis_client.setex(f"reading:{reading_id}", REDIS_TTL_SECONDS, 1)

def cache_last_value(sensor_id, data):
    redis_client.set(f"last:{sensor_id}", json.dumps(data))

def get_last_value(sensor_id):
    return redis_client.get(f"last:{sensor_id}")
