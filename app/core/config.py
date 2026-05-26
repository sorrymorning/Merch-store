from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

    DB_TYPE: str = "sqlite"

    # SQLite
    SQLITE_DB: str = "app.db"

    # PostgreSQL
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "app"

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        if self.DB_TYPE == "sqlite":
            return f"sqlite+aiosqlite:///{self.SQLITE_DB}"

        elif self.DB_TYPE == "postgres":
            return (
                f"postgresql+asyncpg://"
                f"{self.POSTGRES_USER}:"
                f"{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_HOST}:"
                f"{self.POSTGRES_PORT}/"
                f"{self.POSTGRES_DB}"
            )

        raise ValueError("Unsupported DB_TYPE")


settings = Settings()