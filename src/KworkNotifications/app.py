import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from KworkNotifications.core import models
from KworkNotifications.tgbot import services


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Lifespan startup: initialization")
    app.state.bg_tasks = []
    await models.init()
    await services.start_services(app)
    logger.info("All services started")

    logger.info("Lifespan startup complete, entering yield")
    try:
        yield
    finally:
        logger.info("Lifespan shutdown: stopping bg tasks and scheduler")

        for t, obj in list(app.state.bg_tasks):
            if not t.done():
                t.cancel()

        await asyncio.sleep(0.1)

        for t, obj in list(app.state.bg_tasks):
            if obj and hasattr(obj, "close"):
                try:
                    await asyncio.wait_for(obj.close(), timeout=2)
                except (asyncio.TimeoutError, Exception) as e:
                    logger.warning(f"Object close failed: {e}")

        for t, _ in list(app.state.bg_tasks):
            try:
                await asyncio.wait_for(t, timeout=3)
            except (asyncio.TimeoutError, asyncio.CancelledError):
                pass
            except Exception as e:
                logger.warning(f"Task wait error: {e}")

        logger.info("Shutdown complete")
        tasks = asyncio.all_tasks()
        logger.warning(f"Active tasks at shutdown end: {len(tasks)}")


app = FastAPI(title="KworkNotifications", lifespan=lifespan)
