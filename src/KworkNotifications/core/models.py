import asyncio

from tortoise import Tortoise, fields
from tortoise.models import Model

from KworkNotifications.core.config import database_config


class Users(Model):
    id = fields.IntField(primary_key=True)
    tg_id = fields.BigIntField(db_index=True)

    kwork_credentials: fields.ReverseRelation["KworkCredentials"]

    class Meta:
        table = "users"


class KworkCredentials(Model):
    id = fields.IntField(primary_key=True)
    user = fields.ForeignKeyField("models.Users", related_name="kwork_credentials")
    login = fields.CharField(max_length=255)
    password = fields.CharField(max_length=255)
    last_unread_count = fields.IntField()

    class Meta:
        table = "kwork_credentials"


async def init() -> None:
    await Tortoise.init(config=database_config)
    await Tortoise.generate_schemas()


if __name__ == "__main__":
    asyncio.run(init())
