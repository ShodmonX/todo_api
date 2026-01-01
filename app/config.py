from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DEBUG: bool
    API_TITLE: str
    API_VERSION: str
    DATABASE_URL: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()