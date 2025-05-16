"""Application settings."""

from enum import Enum

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """Environment enum."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # From environment variables
    api_env: Environment = Field(default=Environment.DEVELOPMENT, env="API_ENV")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    secret_key: str = Field(default="default_insecure_key", env="SECRET_KEY")
    postgres_password: str = Field(default="", env="POSTGRES_PASSWORD")

    # From config.yml
    config: dict = {}

    @property
    def app_name(self) -> str:
        """Get application name."""
        return self.config.get("app", {}).get("name", "iot_student_presence_tool")

    @property
    def app_description(self) -> str:
        """Get application description."""
        return self.config.get("app", {}).get(
            "description", "A FastAPI application with ESP32 wifi and cable connection support"
        )

    @property
    def debug(self) -> bool:
        """Get debug mode."""
        return (
            self.config.get("environment", {}).get(self.api_env, {}).get("debug", False)
        )

    @property
    def cors_origins(self) -> list[str]:
        """Get CORS origins."""
        return (
            self.config.get("environment", {})
            .get(self.api_env, {})
            .get("cors_origins", [])
        )

    @property
    def postgres_dsn(self) -> str:
        """Get PostgreSQL connection string."""
        db_config = self.config.get("postgres_db", {})
        user = db_config.get("user", "")
        host = db_config.get("host", "")
        port = db_config.get("port", "5432")
        dbname = db_config.get("dbname", "")

        return f"postgresql://{user}:{self.postgres_password}@{host}:{port}/{dbname}"

    @property
    def esp_32_connection(self) -> str:
        """Get ESP32 connection setting."""
        return self.config.get("esp_32_connection", "wifi")


