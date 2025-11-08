import os

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class TelegramSettings(BaseModel):
    token: str


class DBSettings(BaseModel):
    host: str
    port: int
    user: str
    password: str
    database: str


class ProjectSettings(BaseModel):
    telegram: TelegramSettings
    db: DBSettings

    @classmethod
    def from_env(cls):
        return cls(
            telegram=TelegramSettings(
                token=os.getenv("TELEGRAM__TOKEN", ""),
            ),
            db=DBSettings(
                host=os.getenv("DB__HOST", ""),
                port=int(os.getenv("DB__PORT", "")),
                user=os.getenv("DB__USER", ""),
                password=os.getenv("DB__PASSWORD", ""),
                database=os.getenv("DB__DATABASE", ""),
            ),
        )


settings = ProjectSettings.from_env()
database_config = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": settings.db.host,
                "port": settings.db.port,
                "user": settings.db.user,
                "password": settings.db.password,
                "database": settings.db.database,
            },
        },
    },
    "apps": {
        "models": {
            "models": [
                "KworkNotifications.core.models",
            ],
            "default_connection": "default",
        },
    },
}
