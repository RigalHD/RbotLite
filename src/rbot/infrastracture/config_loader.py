import logging
import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DiscordConfig:
    bot_token: str


@dataclass(frozen=True, slots=True)
class Config:
    discord: DiscordConfig

    @classmethod
    def load_from_env(cls: type["Config"]) -> "Config":
        discord = DiscordConfig(
            bot_token=os.environ["DISCORD_BOT_TOKEN"],
        )
        logging.debug("Конфиг загружен")

        return cls(discord=discord)
