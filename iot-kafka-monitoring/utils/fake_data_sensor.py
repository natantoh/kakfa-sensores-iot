from faker import Faker
import random
from datetime import datetime
from datetime import timezone

fake = Faker()

SENSOR_TYPES = ['temperature', 'humidity', 'pressure', 'light', 'motion', 'co2']

def generate_sensor_data():
    """Gera dados falsos de sensores IoT"""
    sensor_type = random.choice(SENSOR_TYPES)

    data = {
        'sensor_id': fake.uuid4(),
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
    main()