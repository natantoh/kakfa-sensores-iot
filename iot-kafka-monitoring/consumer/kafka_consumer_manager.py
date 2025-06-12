from kafka import KafkaConsumer
from json import loads

class KafkaConsumerManager:
    """
    Responsável por criar e gerenciar o consumidor Kafka para leitura de mensagens de um tópico específico.
    """
    def __init__(self, broker, topic, group_id):
        self.broker = broker
        self.topic = topic
        self.group_id = group_id
        self.consumer = None

    def create_consumer(self):
        """
        Cria e retorna uma instância de KafkaConsumer configurada.
        """
        self.consumer = KafkaConsumer(
            self.topic,
            bootstrap_servers=[self.broker],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id=self.group_id,
            value_deserializer=lambda x: loads(x.decode('utf-8'))
        )
        return self.consumer