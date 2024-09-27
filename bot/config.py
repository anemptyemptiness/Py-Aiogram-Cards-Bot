from aiogram.fsm.storage.redis import Redis
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    TOKEN: str
    YOOTOKEN: str

    REDIS_HOST: str

    # Работа с БД
    DB_NAME: str
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int

    # NATS хост
    NATS_HOST: str

    # NATS для рекламы
    NATS_CONSUMER_SUBJECT_ADV: str
    NATS_STREAM_ADV: str
    NATS_DURABLE_NAME_ADV: str

    # NATS для оплаты
    NATS_CONSUMER_SUBJECT_PAYMENT: str
    NATS_STREAM_PAYMENT: str
    NATS_DURABLE_NAME_PAYMENT: str

    # Данные Robokassa для оплаты
    ROBOKASSA_MERCHANT_LOGIN: str
    ROBOKASSA_TEST_PWD_1: str
    ROBOKASSA_TEST_PWD_2: str
    ROBOKASSA_PROD_PWD_1: str
    ROBOKASSA_PROD_PWD_2: str

    @property
    def get_database_url(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = Settings()
redis = Redis(host=settings.REDIS_HOST)
