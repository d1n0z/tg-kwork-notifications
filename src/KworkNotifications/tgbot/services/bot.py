from dataclasses import dataclass
from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.types import ParseMode

from KworkNotifications.tgbot import handlers

@dataclass
class BotServiceConfig:
    token: str


class BotService:
    def __init__(self, service_config: BotServiceConfig) -> None:
        self._config: BotServiceConfig = service_config
        self._bot: Optional[Bot] = None
        self._dp: Optional[Dispatcher] = None

    @property
    def bot(self) -> Bot:
        if self._bot is None:
            raise RuntimeError("Bot is not initialized. Call initialize() first.")
        return self._bot

    @property
    def dp(self) -> Dispatcher:
        if self._dp is None:
            raise RuntimeError(
                "Dispatcher is not initialized. Call initialize() first."
            )
        return self._dp

    async def initialize(self) -> None:
        self._bot = Bot(
            token=self._config.token,
            parse_mode=str(ParseMode.HTML),
            disable_web_page_preview=True,
        )
        self._dp = Dispatcher(self._bot)

        handlers.register_handlers(self._dp)

    async def run(self) -> None:
        if self._dp is None:
            await self.initialize()
        if self._dp is None:
            raise RuntimeError("The bot or dispatcher failed to initialize.")

        try:
            await self._dp.start_polling(
                allowed_updates=[
                    "message",
                    "callback_query",
                    "message_reaction",
                    "chat_member",
                    "my_chat_member",
                ],
            )
        finally:
            await self.shutdown()

    async def shutdown(self) -> None:
        if self._bot and (session := await self._bot.get_session()) and not session.closed:
            await session.close()
