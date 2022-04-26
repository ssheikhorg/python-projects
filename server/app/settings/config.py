from pydantic import BaseSettings
from dotenv import load_dotenv, find_dotenv
import os
import stripe

load_dotenv(find_dotenv())


class StripeSettings(BaseSettings):
    stripe_secret_key: str = os.getenv('STRIPE_SECRET_KEY')
    stripe_publish_key: str = os.getenv('STRIPE_PUBLISH_KEY')


class ServerSettings(BaseSettings):
    app_name: str = "app_name"
    host: str = os.getenv("host")
    port: int = os.getenv("port")
    debug_mode: bool = os.getenv("debug")


class DatabaseSettings(BaseSettings):
    stripe_db_url: str = os.getenv("stripe_db_url")
    stripe_db_name: str = os.getenv("stripe_db_name")
    yo_launcher_db_url: str = os.getenv("yo_launcher_db_url")
    yo_launcher_db_name: str = os.getenv("yo_launcher_db_name")


class Settings(StripeSettings, ServerSettings, DatabaseSettings):
    pass

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
stripe.api_key = settings.stripe_secret_key
