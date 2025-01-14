from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    ddatabase_url: str = os.getenv("DATABASE_URL")
    database_port: int
    database_username: str
    database_password: str
    database_name: str
    database_url: str = None 
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    
    class Config:
        env_file = ".env"

settings = Settings()