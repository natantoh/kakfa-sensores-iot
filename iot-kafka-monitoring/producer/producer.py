from time import sleep
from json import dumps
from kafka import KafkaProducer
import random
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.fake_data_sensor import generate_sensor_data
from config.settings import settings  # Importa as configurações centralizadas

KAFKA_BROKER = settings.KAFKA_BROKER
TOPIC_NAME = settings.TOPIC_NAME

def create_kafka_producer():
    """Cria e retorna um produtor Kafka"""
    return KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        value_serializer=lambda x: dumps(x).encode('utf-8'),
        api_version=(2, 8, 1),  # Força versão específica
        request_timeout_ms=10000  # Aumenta timeout
    )

def main():
    producer = create_kafka_producer()
    count = 0
    try:
        while True:
            sensor_data = generate_sensor_data()
            count += 1
            print(f"Enviando dados #{count}: {sensor_data}")
            producer.send(TOPIC_NAME, value=sensor_data)
            sleep(random.uniform(0.5, 2)) # Entre 0.5 e 2 segundos entre envios
    except KeyboardInterrupt:
        print(f"Total de mensagens enviadas: {count}")
        print("Parando o producer...")
    finally:
        producer.flush()
        producer.close()

if __name__ == "__main__":
    main()