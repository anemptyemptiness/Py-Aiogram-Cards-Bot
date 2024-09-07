from aiogram.fsm.storage.redis import Redis
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    TOKEN: str
    YOOTOKEN: str

    PATH_TO_PROJECT: str

    REDIS_HOST: str

    DB_NAME: str
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int

    NATS_HOST: str
    NATS_CONSUMER_SUBJECT: str
    NATS_STREAM: str
    NATS_DURABLE_NAME: str

    @property
    def get_database_url(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = Settings()
redis = Redis(host=settings.REDIS_HOST)
