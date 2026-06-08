from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DBPostgresConfigs(BaseSettings):
    model_config = SettingsConfigDict(env_file="docker_compose/.env.postgres",
                                      env_file_encoding="utf-8",
                                      extra="ignore")

    postgres_db_name: str = Field(default="tasks_dev_pgs_db",
                                  alias="POSTGRES_DB_NAME")

    postgres_user: str = Field(default="pgs_dev_user",
                               alias="POSTGRES_USER")

    postgres_password: str = Field(default="pgs_dev_password",
                                   alias="POSTGRES_PASSWORD")

    postgres_host: str = Field(default="127.0.0.1",
                               alias="POSTGRES_HOST")

    postgres_port: int = Field(default=15433,
                               alias="POSTGRES_PORT")

    @property
    def database_url(self) -> str:
        postgres_db_url = ("postgresql+asyncpg://"
                           f"{self.postgres_user}:{self.postgres_password}"
                           f"@{self.postgres_host}:{self.postgres_port}/"
                           f"{self.postgres_db_name}")
        return postgres_db_url

    @property
    def alembic_database_url(self) -> str:
        return self.database_url.replace("%", "%%")


@lru_cache  # App settings cache
def get_postgres_configs() -> DBPostgresConfigs:
    return DBPostgresConfigs()
