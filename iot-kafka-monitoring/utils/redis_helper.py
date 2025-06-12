import redis
import json
import os
import sys

# Garante que o diretório pai está no sys.path para importar config.settings
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.settings import settings

REDIS_HOST = settings.REDIS_HOST
REDIS_PORT = settings.REDIS_PORT
REDIS_TTL_SECONDS = settings.REDIS_TTL_SECONDS

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def is_duplicate(reading_id):
    return redis_client.exists(f"reading:{reading_id}")

def mark_as_processed(reading_id):
    redis_client.setex(f"reading:{reading_id}", REDIS_TTL_SECONDS, 1)

def cache_last_value(sensor_id, data):
    redis_client.set(f"last:{sensor_id}", json.dumps(data))

def get_last_value(sensor_id):
    return redis_client.get(f"last:{sensor_id}")