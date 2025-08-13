from disnake.interactions import AppCmdInter
from disnake.ext import commands


class Ping(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.slash_command(name="ping")
    async def ping(self, inter: AppCmdInter) -> None:
        await inter.response.send_message("Pong!")


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Ping(bot))
