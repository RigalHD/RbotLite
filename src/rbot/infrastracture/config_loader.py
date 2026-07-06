import logging
import os
from dataclasses import dataclass

from sqlalchemy import URL


def str_to_bool(value: str) -> bool:
    return value.lower() in {"1", "true"}


@dataclass(frozen=True, slots=True)
class DatabaseConfig:
    database: str
    username: str
    password: str | None
    host: str = "localhost"
    port: int = 5432
    debug: bool = False

    @classmethod
    def load_from_env(cls: type["DatabaseConfig"]) -> "DatabaseConfig":
        return cls(
            database=os.environ.get("POSTGRES_DATABASE", "postgres"),
            username=os.environ.get("POSTGRES_USERNAME", "postgres"),
            password=os.environ.get("POSTGRES_PASSWORD", "postgres"),
            host=os.environ.get("POSTGRES_HOST", "db"),
            port=int(os.environ.get("POSTGRES_PORT", "5432")),
            debug=str_to_bool(os.environ.get("DB_DEBUG", "false")),
        )

    def build_url(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
        )


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
    database: DatabaseConfig
    discord: DiscordConfig

    @classmethod
    def load_from_env(cls: type["Config"]) -> "Config":
        discord = DiscordConfig(
            bot_token=os.environ["DISCORD_BOT_TOKEN"],
            admin_voice=AdminVoiceConfig.load_from_env(),
        )
        logging.debug("Конфиг загружен")

        return cls(
            database=DatabaseConfig.load_from_env(),
            discord=discord,
        )
