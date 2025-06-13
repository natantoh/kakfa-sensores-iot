import pytest
from unittest.mock import MagicMock
from consumer.sensor_event_processor import SensorEventProcessor

@pytest.fixture
def mock_repository():
    repo = MagicMock()
    repo.conn = MagicMock()
    return repo

@pytest.fixture
def mock_redis_helper():
    return MagicMock()

@pytest.fixture
def processor(mock_repository, mock_redis_helper):
    return SensorEventProcessor(mock_repository, mock_redis_helper)

def test_process_valid_event(processor, mock_repository, mock_redis_helper):
    event = {"unique_reading_id": "abc", "sensor_id": "s1", "sensor_type": "temp"}
    mock_redis_helper.is_duplicate.return_value = False

    processor.process(event)

    mock_redis_helper.is_duplicate.assert_called_once_with("abc")
    mock_repository.insert_sensor_event.assert_called_once_with(event)
    mock_redis_helper.mark_as_processed.assert_called_once_with("abc")
    mock_redis_helper.cache_last_value.assert_called_once_with("s1", event)

def test_process_duplicate_event(processor, mock_repository, mock_redis_helper):
    event = {"unique_reading_id": "abc", "sensor_id": "s1", "sensor_type": "temp"}
    mock_redis_helper.is_duplicate.return_value = True

    processor.process(event)

    mock_repository.insert_sensor_event.assert_not_called()
    mock_redis_helper.mark_as_processed.assert_not_called()
    mock_redis_helper.cache_last_value.assert_not_called()

def test_process_invalid_event(processor, mock_repository, mock_redis_helper):
    event = {"sensor_id": "s1", "sensor_type": "temp"}  # falta unique_reading_id

    processor.process(event)

    mock_repository.insert_sensor_event.assert_not_called()
    mock_redis_helper.mark_as_processed.assert_not_called()
    mock_redis_helper.cache_last_value.assert_not_called()

def test_process_rollback_on_exception(processor, mock_repository, mock_redis_helper):
    event = {"unique_reading_id": "abc", "sensor_id": "s1", "sensor_type": "temp"}
    mock_redis_helper.is_duplicate.return_value = False
    mock_repository.insert_sensor_event.side_effect = Exception("DB error")

    processor.process(event)

    mock_repository.conn.rollback.assert_called_once()