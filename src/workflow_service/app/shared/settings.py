from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = (
        "postgresql+psycopg://postgres:postgres@localhost:5435/workflows"
    )
    rabbitmq_url: str = "amqp://guest:guest@localhost/"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
