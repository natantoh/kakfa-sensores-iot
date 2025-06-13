import pytest
from unittest.mock import MagicMock, patch
from consumer.sensor_event_repository import SensorEventRepository
from datetime import datetime

@pytest.fixture
def db_config():
    return {
        'dbname': 'iotdata',
        'user': 'iotuser',
        'password': 'iotpassword',
        'host': 'localhost',
        'port': 5432
    }

@pytest.fixture
def repository(db_config):
    return SensorEventRepository(db_config)

def test_connect_and_create_schema(repository):
    with patch('consumer.sensor_event_repository.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        repository.create_database_schema = MagicMock()

        repository.connect()

        mock_connect.assert_called_once_with(**repository.db_config)
        repository.create_database_schema.assert_called_once()

def test_insert_sensor_event_commits(repository):
    # Monta um sensor_data de exemplo
    sensor_data = {
        'unique_reading_id': 'abc-123',
        'sensor_id': 'sensor-1',
        'sensor_type': 'temperature',
        'location': {'latitude': 10.0, 'longitude': 20.0},
        'timestamp': datetime.now().isoformat(),
        'value': 25.5,
        'unit': 'C',
        'status': 'active',
        'battery_level': 90
    }
    # Mock da conexão e cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    repository.conn = mock_conn

    repository.insert_sensor_event(sensor_data)

    assert mock_cursor.execute.call_count == 1
    mock_conn.commit.assert_called_once()

def test_close_closes_connection(repository):
    mock_conn = MagicMock()
    repository.conn = mock_conn

    repository.close()

    mock_conn.close.assert_called_once()