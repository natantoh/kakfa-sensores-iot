import logging
from utils.redis_helper import RedisHelper
from config.settings import settings

logger = logging.getLogger(__name__)

class SensorEventProcessor:
    """
    Responsável por processar eventos de sensores recebidos do Kafka:
    - Verifica duplicidade usando Redis
    - Persiste o evento no banco de dados via repositório
    - Atualiza o cache do último valor do sensor
    """
    def __init__(self, repository, redis_helper=None):
        self.repository = repository
        # Permite injeção para testes, mas usa padrão do settings se não for passado
        self.redis_helper = redis_helper or RedisHelper()

    def process(self, sensor_data):
        """
        Processa uma mensagem de evento de sensor, aplicando deduplicação,
        persistência e cache.
        """
        reading_id = sensor_data.get("unique_reading_id")
        sensor_id = sensor_data.get("sensor_id")

        if not reading_id or not sensor_id:
            logger.warning("Mensagem inválida, ignorando.")
            return

        if self.redis_helper.is_duplicate(reading_id):
            logger.info(f"Mensagem duplicada ignorada: {reading_id}")
            return

        logger.info(f"Mensagem recebida: {sensor_id} - {sensor_data['sensor_type']}")

        try:
            self.repository.insert_sensor_event(sensor_data)
            self.redis_helper.mark_as_processed(reading_id)
            self.redis_helper.cache_last_value(sensor_id, sensor_data)
            logger.info("Dados processados e armazenados com sucesso")
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            self.repository.conn.rollback()