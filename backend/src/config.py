from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""

    # Database
    database_path: str = "data/gasmap.db"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # API
    api_prefix: str = "/api"
    app_name: str = "GasMap API"
    app_version: str = "0.1.0"

    # Simulation defaults
    default_grid_resolution: int = 200
    default_grid_size: float = 5000.0  # meters

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()