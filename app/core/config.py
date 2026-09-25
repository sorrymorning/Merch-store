from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field


from typing import Literal

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    DB_TYPE: Literal["sqlite", "postgres"] = "sqlite"

    SQLITE_DB: str = "app.db"

    POSTGRESS_DB_USER: str = "postgres"
    POSTGRESS_DB_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRESS_DB_HOST_PORT: int = 5432
    POSTGRES_DB: str = "app"

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        if self.DB_TYPE == "sqlite":
            return f"sqlite+aiosqlite:///{self.SQLITE_DB}"

        return (
            f"postgresql+asyncpg://"
            f"{self.POSTGRESS_DB_USER}:"
            f"{self.POSTGRESS_DB_PASSWORD}@"
            f"{self.POSTGRES_HOST}:"
            f"{self.POSTGRESS_DB_HOST_PORT}/"
            f"{self.POSTGRES_DB}"
        )


settings = Settings(_env_file=".env")