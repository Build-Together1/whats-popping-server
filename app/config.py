from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # DATABASE CONFIG
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_HOSTNAME: str
    DB_PORT: str
    DB_NAME: str

    # AUTH CONFIG
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    OTP_CODE_LENGTH: int
    PASSWORD_LENGTH: int
    TOKEN_URL: str

    # GOOGLE AUTH CONFIG
    CLIENT_ID: str
    CLIENT_SECRET: str
    CONF_URL: str
    NAME: str
    AUTHORIZE_URL: str
    ACCESS_TOKEN_URL: str

    # EMAIL CONFIG
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_TLS: bool
    MAIL_SSL: bool
    USE_CREDENTIALS: bool
    VALIDATE_CERTS: bool

    # APP CONFIG


model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


@lru_cache()
def get_settings() -> Settings:
    setting = Settings(_env_file='.env', _env_file_encoding='utf-8')
    return setting


settings = get_settings()





