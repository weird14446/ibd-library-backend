from pathlib import Path
from urllib.parse import quote_plus
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

# .env 파일 경로
ENV_FILE = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # Database
    database_host: str = "localhost"
    database_port: int = 3306
    database_name: str = "ibd_library"
    database_user: str = "root"
    database_password: str = ""
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    
    @property
    def database_url(self) -> str:
        # 특수문자 URL 인코딩
        encoded_password = quote_plus(self.database_password)
        return f"mysql+pymysql://{self.database_user}:{encoded_password}@{self.database_host}:{self.database_port}/{self.database_name}"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
