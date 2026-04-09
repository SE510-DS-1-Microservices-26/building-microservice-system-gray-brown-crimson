import os


class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/polling"
    )
    users_service_url: str = os.getenv(
        "USERS_SERVICE_URL", "http://localhost:8001/api/v2/users"
    )


settings = Settings()
