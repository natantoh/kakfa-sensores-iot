import time
import pytest
from utils.redis_helper import RedisHelper

@pytest.fixture
def redis_helper():
    # Use um Redis local de teste, com TTL curto para facilitar os testes
    return RedisHelper(host='localhost', port=6379, ttl=2)

def test_mark_and_check_duplicate(redis_helper):
    reading_id = "pytest-unique-id"
    # Deve não existir inicialmente
    assert not redis_helper.is_duplicate(reading_id)
    # Marca como processado
    redis_helper.mark_as_processed(reading_id)
    # Agora deve ser duplicado
    assert redis_helper.is_duplicate(reading_id)

def test_duplicate_expires(redis_helper):
    reading_id = "pytest-expire-id"
    redis_helper.mark_as_processed(reading_id)
    assert redis_helper.is_duplicate(reading_id)
    # Espera o TTL expirar
    time.sleep(3)
    # Agora não deve mais ser duplicado
    assert not redis_helper.is_duplicate(reading_id)

def test_cache_last_value_and_get(redis_helper):
    sensor_id = "pytest-sensor"
    data = {"value": 42, "unit": "C"}
    redis_helper.cache_last_value(sensor_id, data)
    result = redis_helper.get_last_value(sensor_id)
    assert result is not None
    # O valor retornado é uma string JSON, então pode comparar assim:
    import json
    assert json.loads(result) == data