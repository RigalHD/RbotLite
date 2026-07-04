import logging

from disnake import Embed
from disnake.ext import commands
from disnake.ext.commands import Bot, Context
from disnake.interactions import ApplicationCommandInteraction

X_COORDINATE_PARAM = commands.Param(description="Координата x")
Z_COORDINATE_PARAM = commands.Param(description="Координата z")
TO_OVERWORLD_PARAM = commands.Param(
    default=False,
    description="Если True - конвертирует адские координаты в координаты верхнего мира",
)


class Misc(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.slash_command(
        name="n_calc",
        description="Рассчитает ваши координаты в аду или обычном мире",
    )
    async def n_calc(
        self,
        interaction: ApplicationCommandInteraction[Bot],
        x: int = X_COORDINATE_PARAM,
        z: int = Z_COORDINATE_PARAM,
        to_overworld: bool = TO_OVERWORLD_PARAM,
    ) -> None:
        await interaction.response.defer()

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

        await interaction.edit_original_response(
            embed=Embed(title=message, description=result, color=color),
        )

    @commands.slash_command(name="ping", description="Проверка отклика бота")
    async def ping(self, interaction: ApplicationCommandInteraction[Bot]) -> None:
        await interaction.response.defer()
        await interaction.edit_original_response(content="Pong!")

    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx: Context[Bot]) -> None:
        await ctx.reply("Slash-команды синхронизируются disnake автоматически при запуске.")

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


def setup(bot: Bot) -> None:
    bot.add_cog(Misc(bot))
