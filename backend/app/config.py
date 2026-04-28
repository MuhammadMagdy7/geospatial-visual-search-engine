# from pydantic_settings import BaseSettings, SettingsConfigDict
# from pydantic import field_validator
# from typing import List

# class Settings(BaseSettings):
#     DATABASE_URL: str
#     GOOGLE_MAPS_API_KEY: str = ""
#     BACKEND_HOST: str = "0.0.0.0"
#     BACKEND_PORT: int = 8000
#     CORS_ORIGINS: List[str] = ["http://localhost:5173"]

#     @field_validator("CORS_ORIGINS", mode="before")
#     @classmethod
#     def parse_cors(cls, v):
#         if isinstance(v, str):
#             return [origin.strip() for origin in v.split(",")]
#         return v

#     model_config = SettingsConfigDict(env_file=".env", extra="ignore")

# settings = Settings()


# backend/app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    DATABASE_URL: str
    GOOGLE_MAPS_API_KEY: str = ""
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()