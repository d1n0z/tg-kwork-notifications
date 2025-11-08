import asyncio

from fastapi import FastAPI
from loguru import logger

from KworkNotifications.core import config
from KworkNotifications.tgbot.services.bot import BotService, BotServiceConfig
from KworkNotifications.tgbot.services.monitoring import monitor_kwork

services = [
    monitor_kwork,
]
class_services = [
    bot_service := BotService(BotServiceConfig(token=config.settings.telegram.token)),
]


async def start_services(app: FastAPI):
    for service in services:
        service_task = asyncio.create_task(service(), name=service.__name__)
        app.state.bg_tasks.append((service_task, None))
        logger.info(f"Started service {service.__name__}")
    for service in class_services:
        if hasattr(service, "initialize"):
            await service.initialize()
        service_task = asyncio.create_task(
            service.run(), name=service.__class__.__name__
        )
        app.state.bg_tasks.append((service_task, None))
        logger.info(f"Started service {service.__class__.__name__}")
