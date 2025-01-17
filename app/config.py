from pydantic_settings import BaseSettings
import os
from typing import Optional

class Settings(BaseSettings):
    database_url: Optional[str] = None
    database_hostname: str
    database_port: int
    database_username: str
    database_password: str
    database_name: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    
    class Config:
        env_file = ".env"

settings = Settings()