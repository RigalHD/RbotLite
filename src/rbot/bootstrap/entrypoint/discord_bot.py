import asyncio
import logging
from pathlib import Path

from disnake import Game, Intents, Status
from disnake.ext.commands import Bot, CommandSyncFlags

from rbot.infrastracture.config_loader import Config
from rbot.infrastracture.database import check_database_connection, create_database_engine


async def main(_argv: list[str] | None = None) -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    command_sync_flags = CommandSyncFlags.default()
    command_sync_flags.allow_command_deletion = False

    bot = Bot(
        command_prefix="!!",
        activity=Game("NewSide"),
        command_sync_flags=command_sync_flags,
        intents=Intents.all(),
        status=Status.idle,
    )

    config = Config.load_from_env()
    database_engine = create_database_engine(config.database)

    cogs_dir = Path(__file__).parent.parent.parent / "presentation" / "discord_bot" / "cogs"

    try:
        await check_database_connection(database_engine)
        logger.info("Connected to database successfully.")

        for file in cogs_dir.glob("*.py"):
            if file.name != "__init__.py":
                bot.load_extension(f"rbot.presentation.discord_bot.cogs.{file.stem}")

        await bot.start(config.discord.bot_token)
    finally:
        if not bot.is_closed():
            await bot.close()
        await database_engine.dispose()


def run_discord_bot(args: list[str] | None = None) -> None:
    asyncio.run(main(args))


if __name__ == "__main__":
    run_discord_bot()
