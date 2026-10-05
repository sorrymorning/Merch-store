from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field


from typing import Literal

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Registration Settings
    SECRET_KEY: str = "super_secret_key"
    ALGORITHM: str = "HS256"
    # Database Settings
    DB_TYPE: Literal["sqlite", "postgres"] = "sqlite"

    SQLITE_DB: str = "app.db"

    POSTGRESS_DB_USER: str = "postgres"
    POSTGRESS_DB_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRESS_DB_HOST_PORT: int = 5432
    POSTGRES_DB: str = "app"

    # Redis Settings
    REDIS_HOST: str = "localhost"    
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None
    

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


    @computed_field
    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


settings = Settings(_env_file=".env")
