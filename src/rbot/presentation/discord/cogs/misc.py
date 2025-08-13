from discord import Embed, Interaction, app_commands
from discord.ext import commands
from discord.ext.commands import Bot


class Misc(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="n_calc",
        description="Рассчитает ваши координаты в аду",
    )
    async def n_calc(
        self,
        interaction: Interaction,
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

    @app_commands.command(name="ping")
    async def ping(self, inter: Interaction) -> None:
        await inter.response.send_message("Pong!")

    @commands.hybrid_command()
    @commands.is_owner()
    async def sync(self, inter: Interaction) -> None:
        await inter.message.reply("Синхронизация идет...")
        await self.bot.tree.sync()
        await inter.message.reply("Успех")

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print("Бот готов")


async def setup(bot: Bot) -> None:
    await bot.add_cog(Misc(bot))
