import asyncio
import random

from kwork import Kwork
from loguru import logger

from KworkNotifications.core.models import Users
from KworkNotifications.tgbot import services


def pluralize_messages(count: int) -> str:
    if count % 10 == 1 and count % 100 != 11:
        return f"{count} новое сообщение"
    elif count % 10 in (2, 3, 4) and count % 100 not in (12, 13, 14):
        return f"{count} новых сообщения"
    else:
        return f"{count} новых сообщений"


async def monitor_kwork():
    while True:
        try:
            users = await Users.all().prefetch_related("kwork_credentials")

            for user in users:
                if not user.kwork_credentials:
                    continue
                for credentials in user.kwork_credentials:
                    api = None
                    try:
                        api = Kwork(
                            login=credentials.login, password=credentials.password
                        )
                        dialogs = await api.get_all_dialogs()
                        unread_count = 0
                        for dialog in dialogs:
                            unread_count += dialog.unread_count or 0
                        if unread_count != credentials.last_unread_count:
                            if credentials.last_unread_count < unread_count:
                                await services.bot_service.bot.send_message(
                                    chat_id=(await credentials.user).tg_id,
                                    text=f'У вас <a href="https://kwork.ru/inbox">{pluralize_messages(unread_count)}</a>.',
                                )
                            credentials.last_unread_count = unread_count
                            await credentials.save()
                    except Exception:
                        logger.exception(
                            f"Error monitoring credentials {credentials.login}:"
                        )
                    finally:
                        if api:
                            try:
                                await api.close()
                            except Exception:
                                pass
        except Exception:
            logger.exception("Error in monitoring loop")

        await asyncio.sleep(random.randint(200, 600))
