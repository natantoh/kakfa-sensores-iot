from faker import Faker
import random
from datetime import datetime, timezone
import os

fake = Faker()

SENSOR_TYPES = ['temperature', 'humidity', 'pressure', 'light', 'motion', 'co2']

# Pool para IDs já gerados
_id_pool = []
_counter = 0

def generate_sensor_data():
    """Gera dados falsos de sensores IoT, com opção de duplicar IDs para teste"""
    global _id_pool, _counter
    _counter += 1

    sensor_type = random.choice(SENSOR_TYPES)

    # Ative duplicatas para teste via variável de ambiente
    enable_duplicates = os.getenv('ENABLE_DUPLICATES', 'true').lower() == 'true'

    if enable_duplicates and _counter % 4 == 0 and _id_pool:
        # A cada 4 mensagens, repete um ID antigo
        unique_reading_id = random.choice(_id_pool)
    else:
        unique_reading_id = str(fake.uuid4())
        _id_pool.append(unique_reading_id)
        if len(_id_pool) > 20:
            _id_pool.pop(0)

    data = {
        'unique_reading_id': unique_reading_id,
        'sensor_id': str(fake.uuid4()),
        'sensor_type': sensor_type,
        'location': {
            'latitude': float(fake.latitude()),
            'longitude': float(fake.longitude())
        },
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'value': generate_sensor_value(sensor_type),
        'unit': get_unit_for_sensor(sensor_type),
        'status': random.choice(['active', 'inactive', 'error']),
        'battery_level': random.randint(0, 100)
    }

    return data

def generate_sensor_value(sensor_type):
    """Gera valores realistas baseados no tipo de sensor"""
    if sensor_type == 'temperature':
        return round(random.uniform(-10, 50), 2)
    elif sensor_type == 'humidity':
        return random.randint(0, 100)
    elif sensor_type == 'pressure':
        return round(random.uniform(900, 1100), 2)
    elif sensor_type == 'light':
        return random.randint(0, 1000)
    elif sensor_type == 'motion':
        return random.choice([0, 1])
    elif sensor_type == 'co2':
        return random.randint(300, 2000)
    else:
        return random.random()

def get_unit_for_sensor(sensor_type):
    """Retorna a unidade de medida para cada tipo de sensor"""
    units = {
        'temperature': 'C',
        'humidity': '%',
        'pressure': 'hPa',
        'light': 'lux',
        'motion': 'bool',
        'co2': 'ppm'
    }
    return units.get(sensor_type, 'unknown')

def main():
    data = generate_sensor_data()
    print(f"Dados do sensor: {data}")

if __name__ == "__main__":
    for _ in range(20):
        data = generate_sensor_data()
        print(f"Dados do sensor: {data}")