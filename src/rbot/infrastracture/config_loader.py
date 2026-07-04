import logging
import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AdminVoiceConfig:
    guild_id: int
    admin_role_id: int
    channel_id: int
    request_cooldown_seconds: int

    @classmethod
    def load_from_env(cls: type["AdminVoiceConfig"]) -> "AdminVoiceConfig":
        return cls(
            guild_id=int(os.environ["DISCORD_ADMIN_VOICE_GUILD_ID"]),
            admin_role_id=int(os.environ["DISCORD_ADMIN_VOICE_ROLE_ID"]),
            channel_id=int(os.environ["DISCORD_ADMIN_VOICE_CHANNEL_ID"]),
            request_cooldown_seconds=int(
                os.environ["DISCORD_ADMIN_VOICE_REQUEST_COOLDOWN_SECONDS"],
            ),
        )


@dataclass(frozen=True, slots=True)
class DiscordConfig:
    bot_token: str
    admin_voice: AdminVoiceConfig


@dataclass(frozen=True, slots=True)
class Config:
    discord: DiscordConfig

    @classmethod
    def load_from_env(cls: type["Config"]) -> "Config":
        discord = DiscordConfig(
            bot_token=os.environ["DISCORD_BOT_TOKEN"],
            admin_voice=AdminVoiceConfig.load_from_env(),
        )
        logging.debug("Конфиг загружен")

        return cls(discord=discord)
