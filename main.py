from Rbot import RBot
from dotenv import load_dotenv
import disnake
import os


def main() -> None:
    load_dotenv(".env")

    bot = RBot(
        command_prefix="!!",
        help_command=None,
        activity=disnake.Game("NewSide"),
        intents=disnake.Intents.all(),
        status=disnake.Status.idle,
        test_guilds=[1097125882876923954, 1117027821827670089],
    )

    for file in os.listdir("./cogs"):
        if file.endswith(".py") and file != "__init__.py":
            bot.load_extension(f"cogs.{file[:-3]}")

    bot.run(os.getenv("RBOT_TOKEN"))


if __name__ == "__main__":
    main()
