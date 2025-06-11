from sqlalchemy import create_engine, Column, String, Float, Table, MetaData
from config.settings import DB_PATH

engine = create_engine(f'sqlite:///{DB_PATH}', echo=True)
metadata = MetaData()

sensor_data = Table(
    'sensor_data', metadata,
    Column('device_id', String),
    Column('temperature', Float),
    Column('humidity', Float),
    Column('timestamp', String)
)

def create_tables():
    metadata.create_all(engine)
