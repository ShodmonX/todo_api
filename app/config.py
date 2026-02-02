from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, Field

class Settings(BaseSettings):
    DEBUG: bool
    API_TITLE: str
    API_VERSION: str
    DATABASE_URL: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    MAILTRAP_API_TOKEN: str
    MEDIA_ROOT: str = "media/attachments"
    ALLOWED_ORIGINS: str = ""
    
    @property
    def allowed_origins_list(self) -> list[str]:
        s = self.ALLOWED_ORIGINS.strip()
        if not s:
            return []
        return [x.strip() for x in s.split(",") if x.strip()]
    
    model_config = SettingsConfigDict(env_file=".env", from_attributes=True)

settings = Settings() # type: ignore