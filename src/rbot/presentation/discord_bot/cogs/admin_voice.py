import math
import time

from disnake import AllowedMentions, ButtonStyle, HTTPException, Member, VoiceChannel, ui
from disnake.ext import commands
from disnake.ext.commands import Bot
from disnake.interactions import ApplicationCommandInteraction, MessageInteraction

GUILD_ID = 1147831863054979072
ADMIN_ROLE_ID = 1147899870372442134
ADMIN_VOICE_CHANNEL_ID = 1188853642690842634
REQUEST_COOLDOWN_SECONDS = 60


class AdminVoiceRequestView(ui.View):
    def __init__(self, requester: Member, admin_voice_channel: VoiceChannel) -> None:
        super().__init__(timeout=300)
        self.requester = requester
        self.admin_voice_channel = admin_voice_channel

    async def interaction_check(self, interaction: MessageInteraction[Bot]) -> bool:
        member = interaction.author
        if not isinstance(member, Member) or ADMIN_ROLE_ID not in {
            role.id for role in member.roles
        }:
            await interaction.response.send_message(
                "Эти кнопки доступны только администраторам.",
                ephemeral=True,
            )
            return False
        return True

    def disable_buttons(self) -> None:
        for item in self.children:
            if isinstance(item, ui.Button):
                item.disabled = True

    @ui.button(label="Переносить", style=ButtonStyle.green)
    async def move_user(
        self,
        _button: ui.Button["AdminVoiceRequestView"],
        interaction: MessageInteraction[Bot],
    ) -> None:
        if self.requester.voice is None:
            await interaction.response.send_message(
                "Пользователь уже вышел из голосового канала.",
                ephemeral=True,
            )
            return

        try:
            await self.requester.move_to(
                self.admin_voice_channel,
                reason=f"Запрос подтверждён администратором {interaction.author}",
            )
        except HTTPException:
            await interaction.response.send_message(
                "Не удалось перенести пользователя. Проверьте права бота и попробуйте снова.",
                ephemeral=True,
            )
            return
        self.disable_buttons()
        self.stop()
        await interaction.response.edit_message(
            content=(
                f"{self.requester.mention} перенесён в {self.admin_voice_channel.mention} "
                f"администратором {interaction.author.mention}."
            ),
            view=self,
        )

    @ui.button(label="Не переносить", style=ButtonStyle.red)
    async def reject_request(
        self,
        _button: ui.Button["AdminVoiceRequestView"],
        interaction: MessageInteraction[Bot],
    ) -> None:
        self.disable_buttons()
        self.stop()
        await interaction.response.edit_message(
            content=(
                f"Запрос {self.requester.mention} отклонён "
                f"администратором {interaction.author.mention}."
            ),
            view=self,
        )


class AdminVoice(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.last_request_at: dict[int, float] = {}

    @commands.slash_command(
        name="admin_voice",
        description="Попросить администраторов перенести вас в админский войс",
        guild_ids=[GUILD_ID],
    )
    async def admin_voice(
        self,
        interaction: ApplicationCommandInteraction[Bot],
    ) -> None:
        if interaction.guild_id != GUILD_ID or interaction.guild is None:
            await interaction.response.send_message(
                "Эта команда доступна только на основном сервере.",
                ephemeral=True,
            )
            return

        author = interaction.author
        if not isinstance(author, Member) or author.voice is None:
            await interaction.response.send_message(
                "Сначала подключитесь к голосовому каналу.",
                ephemeral=True,
            )
            return

        if author.voice.channel is not None and author.voice.channel.id == ADMIN_VOICE_CHANNEL_ID:
            await interaction.response.send_message(
                "Вы уже находитесь в админском голосовом канале.",
                ephemeral=True,
            )
            return

        admin_role = interaction.guild.get_role(ADMIN_ROLE_ID)
        admin_voice_channel = interaction.guild.get_channel(ADMIN_VOICE_CHANNEL_ID)
        if admin_role is None or not isinstance(admin_voice_channel, VoiceChannel):
            await interaction.response.send_message(
                "Не удалось найти роль администраторов или админский голосовой канал.",
                ephemeral=True,
            )
            return

        now = time.monotonic()
        retry_after = REQUEST_COOLDOWN_SECONDS - (
            now - self.last_request_at.get(author.id, -REQUEST_COOLDOWN_SECONDS)
        )
        if retry_after > 0:
            await interaction.response.send_message(
                f"Повторный запрос можно отправить через {math.ceil(retry_after)} сек.",
                ephemeral=True,
            )
            return

        self.last_request_at[author.id] = now
        await interaction.response.send_message(
            f"{admin_role.mention}, {author.mention} просит перенести его "
            f"в {admin_voice_channel.mention}.",
            allowed_mentions=AllowedMentions(roles=[admin_role], users=[author]),
            view=AdminVoiceRequestView(author, admin_voice_channel),
        )


def setup(bot: Bot) -> None:
    bot.add_cog(AdminVoice(bot))
