from app.core.configs_postgres import DBPostgresConfigs


def test_database_url_is_built_from_postgres_environment_values() -> None:
    settings = DBPostgresConfigs(
        POSTGRES_DB_NAME="custom_db",
        POSTGRES_USER="custom_user",
        POSTGRES_PASSWORD="custom_password",
        POSTGRES_HOST="192.0.2.10",
        POSTGRES_PORT=25432,
    )

    assert settings.database_url == (
        "postgresql+asyncpg://custom_user:custom_password@192.0.2.10:25432/custom_db"
    )
