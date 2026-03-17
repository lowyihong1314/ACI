import os


BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


class BaseConfig:
    SECRET_KEY = require_env("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = require_env("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }
    JWT_SECRET_KEY = require_env("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "86400"))
    DEFAULT_ADMIN_USERNAME = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
    DEFAULT_ADMIN_PASSWORD = require_env("DEFAULT_ADMIN_PASSWORD")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
    JSON_SORT_KEYS = False
    ENV_NAME = "base"


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    ENV_NAME = "development"


class ProductionConfig(BaseConfig):
    DEBUG = False
    ENV_NAME = "production"


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "dev": DevelopmentConfig,
    "production": ProductionConfig,
    "prod": ProductionConfig,
}


def get_config(config_name: str | None = None):
    env_name = config_name or os.getenv("FLASK_ENV", "development")
    return CONFIG_MAP.get(env_name.lower(), DevelopmentConfig)
