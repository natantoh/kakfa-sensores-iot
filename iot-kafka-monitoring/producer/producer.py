from time import sleep
from json import dumps
from kafka import KafkaProducer
import random
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.fake_data_sensor import generate_sensor_data
from config.settings import settings  # Importa as configurações centralizadas

class IoTSensorProducer:
    def __init__(self, broker, topic):
        self.broker = broker
        self.topic = topic
        self.producer = self._create_kafka_producer()
        self.count = 0

    def _create_kafka_producer(self):
        return KafkaProducer(
            bootstrap_servers=[self.broker],
            value_serializer=lambda x: dumps(x).encode('utf-8'),
            api_version=(2, 8, 1),
            request_timeout_ms=10000
        )

    def send_sensor_data(self):
        sensor_data = generate_sensor_data()
        self.count += 1
        print(f"Enviando dados #{self.count}: {sensor_data}")
        self.producer.send(self.topic, value=sensor_data)

    def run(self):
        try:
            while True:
                self.send_sensor_data()
                sleep(random.uniform(0.5, 2))
        except KeyboardInterrupt:
            print(f"Total de mensagens enviadas: {self.count}")
            print("Parando o producer...")
        finally:
            self.producer.flush()
            self.producer.close()

if __name__ == "__main__":
    producer = IoTSensorProducer(
        broker=settings.KAFKA_BROKER,
        topic=settings.TOPIC_NAME
    )
    producer.run()