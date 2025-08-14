import logging

from discord import Embed, Interaction, app_commands
from discord.ext import commands
from discord.ext.commands import Bot, Context


class Misc(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="n_calc",
        description="Рассчитает ваши координаты в аду или обычном мире",
    )
    @app_commands.describe(
        x="Координата x",
        z="Координата z",
        to_overworld="Если True - конвертирует адские координаты в координаты верхнего мира",
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
            color = 0xFF0000
        else:
            message = "Координаты по обычному миру:"
            x_overworld = x * 8
            z_overworld = z * 8
            result = f"x = {x_overworld} | z = {z_overworld}"
            color = 0x14AB00

        await interaction.response.send_message(embed=Embed(title=message, description=result, color=color))

    @app_commands.command(name="ping", description="Проверка отклика бота")
    async def ping(self, interaction: Interaction) -> None:
        await interaction.response.send_message("Pong!")

    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx: Context[Bot]) -> None:
        await ctx.reply("Синхронизация идет...")
        await self.bot.tree.sync()
        await ctx.reply("Успех")

    @commands.command()
    @commands.is_owner()
    async def emergency_shutdown(self, ctx: Context[Bot]) -> None:
        await ctx.reply("Экстренное выключение...")
        message = f"Бот остановлен командой пользователя {ctx.author.id}"

        await self.bot.close()
        logging.info(message)

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        message = f"Бот успешно запущен {self.bot.user}"
        logging.info(message)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Misc(bot))
