from disnake import Member, Permissions, TextChannel
from disnake.ext import commands
from disnake.ext.commands import Bot
from disnake.flags import InteractionContextTypes
from disnake.interactions import ApplicationCommandInteraction

from rbot.presentation.discord_bot.embed_builder import EmbedSetupView, parse_color

DEFAULT_EMBED_COLOR = "#00A2FF"

COLOR_PARAM = commands.Param(
    default=DEFAULT_EMBED_COLOR,
    description="Цвет боковой полосы в формате #RRGGBB",
)
CHANNEL_PARAM = commands.Param(description="Канал для публикации сообщения")


class EmbedBuilder(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.slash_command(
        name="embed",
        description="Создать и опубликовать embed-сообщение",
        contexts=InteractionContextTypes(guild=True),
        default_member_permissions=Permissions(administrator=True),
    )
    async def embed(
        self,
        interaction: ApplicationCommandInteraction[Bot],
        channel: TextChannel = CHANNEL_PARAM,
        color: str = COLOR_PARAM,
    ) -> None:
        author = interaction.author
        if not isinstance(author, Member) or not author.guild_permissions.administrator:
            await interaction.response.send_message(
                "Команда доступна только администраторам.",
                ephemeral=True,
            )
            return

        try:
            parsed_color = parse_color(color)
        except ValueError:
            await interaction.response.send_message(
                "Цвет должен быть указан в формате #RRGGBB, например #00A2FF.",
                ephemeral=True,
            )
            return

        view = EmbedSetupView(author.id, channel, parsed_color)
        await interaction.response.send_message(
            view.build_summary(),
            view=view,
            ephemeral=True,
        )


def setup(bot: Bot) -> None:
    bot.add_cog(EmbedBuilder(bot))
