import os
from pathlib import Path

from disnake import Game, Intents, Status
from disnake.ext.commands import Bot
from dotenv import load_dotenv


def main() -> None:
    load_dotenv(".env")

    bot = Bot(
        command_prefix="!!",
        help_command=None,
        activity=Game("NewSide"),
        intents=Intents.all(),
        status=Status.idle,
        test_guilds=[1097125882876923954, 1117027821827670089, 1147831863054979072],
    )

    cogs_dir = Path("../../presentation/discord/cogs")

    for file in cogs_dir.glob("*.py"):
        if file.name != "__init__.py":
            bot.load_extension(f"cogs.{file.stem}")

    bot.run(os.getenv("RBOT_TOKEN"))


if __name__ == "__main__":
    main()
