from pydantic import BaseSettings, Field
from typing import Optional


class Settings(BaseSettings):
    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")

    # Application Configuration
    app_name: str = Field(default="Patient Appointment Tracker")
    debug: bool = Field(default=False, env="DEBUG")

    # Database Configuration
    users_file: str = Field(default="users.json")
    appointments_file: str = Field(default="appointments.json")

    # UI Configuration
    page_layout: str = Field(default="wide")
    sidebar_state: str = Field(default="expanded")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()