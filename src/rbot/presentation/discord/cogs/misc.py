from disnake import Embed
from disnake.interactions import AppCmdInter
from disnake.ext import commands
from disnake.ext.commands import Bot


class Misc(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.slash_command(
        name="n_calc",
        description="Рассчитает ваши координаты в аду",
    )
    async def n_calc(
        self,
        interaction: AppCmdInter,
        x: int,
        z: int,
        to_overworld: bool = False,
    ) -> None:
        if not to_overworld:
            message = "Координаты по аду:"
            x_nether = round(x / 8)
            z_nether = round(z / 8)
            result = f"x = {x_nether} | z = {z_nether}"
        else:
            message = "Координаты по обычному миру:"
            x_overworld = round(x / 8)
            z_overworld = round(z / 8)
            result = f"x = {x_overworld} | z = {z_overworld}"

        await interaction.send(embed=Embed(title=message, description=result, color=0x0066FF))


def setup(bot: Bot) -> None:
    bot.add_cog(Misc(bot))
