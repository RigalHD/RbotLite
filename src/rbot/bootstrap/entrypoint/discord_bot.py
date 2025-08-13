import asyncio
import os
from pathlib import Path

from discord import Game, Intents, Status
from discord.ext.commands import Bot
from dotenv import load_dotenv


async def main(_argv: list[str] | None = None) -> None:
    load_dotenv(".env")

    bot = Bot(
        command_prefix="!!",
        activity=Game("NewSide"),
        intents=Intents.all(),
        status=Status.idle,
        test_guilds=[1097125882876923954, 1117027821827670089, 1147831863054979072],
    )

    cogs_dir = Path(__file__).parent.parent.parent / "presentation" / "discord" / "cogs"
    async with bot:
        for file in cogs_dir.glob("*.py"):
            if file.name != "__init__.py":
                await bot.load_extension(f"rbot.presentation.discord.cogs.{file.stem}")
        await bot.start(os.getenv("RBOT_TOKEN"))


def run_discord_bot(args: list[str] | None = None) -> None:
    asyncio.run(main(args))


if __name__ == "__main__":
    run_discord_bot()
