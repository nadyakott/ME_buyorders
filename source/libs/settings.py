from pydantic import BaseSettings, BaseModel

class Settings(BaseSettings):
    """Общие настройки из env."""

    FILE_PATH: str
    APP_NAME: str
    APP_VERSION: str
    BIDDER_PUBKEY: str
    LAMPORT_RATE: int
    MIN_DELTA_PRICE: int
    AUCTION_HOUSE_ADDRESS: str
    TOKEN_MINT: str
    PRIVATE_KEY: str
    URL_MAIN: str = "https://magiceden.io/"


    LOGGER_LEVEL: str = 'INFO'
    LOGGER_DIR: str = '../logs'
    LOGGER_MAX_BYTES: int = 1024 * 1024 * 1024
    LOGGER_BACKUP_COUNT: int = 10
    ADD_TIME: int = 3600

    class Config:
        case_sensitive = True
        env_file = '.env'
        env_file_encoding = 'utf-8'
        env_nested_delimiter = '__'

settings = Settings()