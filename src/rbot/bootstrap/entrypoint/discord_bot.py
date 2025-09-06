import asyncio
import logging
from pathlib import Path

from discord import Game, Intents, Status
from discord.ext.commands import Bot

from rbot.infrastracture.config_loader import Config


async def main(_argv: list[str] | None = None) -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    bot = Bot(
        command_prefix="!!",
        activity=Game("NewSide"),
        intents=Intents.all(),
        status=Status.idle,
    )

    config = Config.load_from_env()

    cogs_dir = Path(__file__).parent.parent.parent / "presentation" / "discord" / "cogs"

    async with bot:
        for file in cogs_dir.glob("*.py"):
            if file.name != "__init__.py":
                await bot.load_extension(f"rbot.presentation.discord.cogs.{file.stem}")

        await bot.start(config.discord.bot_token)


def run_discord_bot(args: list[str] | None = None) -> None:
    asyncio.run(main(args))


if __name__ == "__main__":
    run_discord_bot()
