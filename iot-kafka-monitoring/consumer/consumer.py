import logging
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.settings import settings
from consumer.kafka_consumer_manager import KafkaConsumerManager
from consumer.sensor_event_repository import SensorEventRepository
from consumer.sensor_event_processor import SensorEventProcessor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SensorEventConsumer:
    """
    Orquestra o consumo de mensagens do Kafka, processamento e persistência dos eventos de sensores.
    Responsável por coordenar o fluxo entre o repositório, o consumidor Kafka e o processador de eventos.
    """
    def __init__(self, db_config, kafka_broker, topic_name, group_id):
        self.repository = SensorEventRepository(db_config)
        self.kafka_manager = KafkaConsumerManager(kafka_broker, topic_name, group_id)
        self.processor = SensorEventProcessor(self.repository)

    def run(self):
        """
        Inicia o processo de consumo de mensagens do Kafka, processando e armazenando eventos de sensores.
        """
        try:
            self.repository.connect()
        except Exception as e:
            logger.error(f"Erro ao conectar ao banco de dados: {e}")
            return

        try:
            consumer = self.kafka_manager.create_consumer()
        except Exception as e:
            logger.error(f"Erro ao criar consumidor Kafka: {e}")
            self.repository.close()
            return

        logger.info("Iniciando consumo de mensagens...")

        try:
            for message in consumer:
                sensor_data = message.value
                self.processor.process(sensor_data)
        except KeyboardInterrupt:
            logger.info("Parando o consumer...")
        finally:
            consumer.close()
            self.repository.close()

if __name__ == "__main__":
    consumer = SensorEventConsumer(
        db_config=settings.DB_CONFIG,
        kafka_broker=settings.KAFKA_BROKER,
        topic_name=settings.TOPIC_NAME,
        group_id=settings.GROUP_ID
    )
    consumer.run()