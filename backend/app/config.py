import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)

    # PayPal API Settings
    PAYPAL_MODE: str = Field(default="sandbox")
    PAYPAL_CLIENT_ID: str = Field(default="")
    PAYPAL_CLIENT_SECRET: str = Field(default="")

    @property
    def paypal_base_url(self) -> str:
        if self.PAYPAL_MODE.lower() == "live":
            return "https://api-m.paypal.com"
        return "https://api-m.sandbox.paypal.com"

    @property
    def has_paypal_credentials(self) -> bool:
        return bool(
            self.PAYPAL_CLIENT_ID 
            and self.PAYPAL_CLIENT_SECRET 
            and self.PAYPAL_CLIENT_ID != "your_paypal_sandbox_client_id_here"
        )

    # Policy Defaults
    DEFAULT_MAX_PER_TRANSACTION: float = Field(default=50.00)
    DEFAULT_DAILY_BUDGET: float = Field(default=250.00)
    CURRENCY: str = Field(default="USD")


settings = Settings()
