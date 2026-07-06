import math
import time

from disnake import AllowedMentions, ButtonStyle, HTTPException, Member, VoiceChannel, ui
from disnake.ext import commands
from disnake.ext.commands import Bot
from disnake.interactions import ApplicationCommandInteraction, MessageInteraction

from rbot.infrastracture.config_loader import AdminVoiceConfig

ADMIN_VOICE_CONFIG = AdminVoiceConfig.load_from_env()


class AdminVoiceRequestView(ui.View):
    def __init__(self, requester: Member, admin_voice_channel: VoiceChannel) -> None:
        super().__init__(timeout=300)
        self.requester = requester
        self.admin_voice_channel = admin_voice_channel

    async def interaction_check(self, interaction: MessageInteraction[Bot]) -> bool:
        member = interaction.author
        if not isinstance(member, Member) or ADMIN_VOICE_CONFIG.admin_role_id not in {
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

        await interaction.response.defer()
        try:
            await self.requester.move_to(
                self.admin_voice_channel,
                reason=f"Запрос подтверждён администратором {interaction.author}",
            )
        except HTTPException:
            await interaction.followup.send(
                "Не удалось перенести пользователя. Проверьте права бота и попробуйте снова.",
                ephemeral=True,
            )
            return
        self.disable_buttons()
        self.stop()
        await interaction.edit_original_response(
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
        guild_ids=[ADMIN_VOICE_CONFIG.guild_id],
    )
    async def admin_voice(
        self,
        interaction: ApplicationCommandInteraction[Bot],
    ) -> None:
        await interaction.response.defer(ephemeral=True)

        if interaction.guild_id != ADMIN_VOICE_CONFIG.guild_id or interaction.guild is None:
            await interaction.edit_original_response(
                content="Эта команда доступна только на основном сервере.",
            )
            return

        author = interaction.author
        if not isinstance(author, Member) or author.voice is None:
            await interaction.edit_original_response(
                content="Сначала подключитесь к голосовому каналу.",
            )
            return

        if (
            author.voice.channel is not None
            and author.voice.channel.id == ADMIN_VOICE_CONFIG.channel_id
        ):
            await interaction.edit_original_response(
                content="Вы уже находитесь в админском голосовом канале.",
            )
            return

        admin_role = interaction.guild.get_role(ADMIN_VOICE_CONFIG.admin_role_id)
        admin_voice_channel = interaction.guild.get_channel(ADMIN_VOICE_CONFIG.channel_id)
        if admin_role is None or not isinstance(admin_voice_channel, VoiceChannel):
            await interaction.edit_original_response(
                content="Не удалось найти роль администраторов или админский голосовой канал.",
            )
            return

        now = time.monotonic()
        retry_after = ADMIN_VOICE_CONFIG.request_cooldown_seconds - (
            now
            - self.last_request_at.get(
                author.id,
                -ADMIN_VOICE_CONFIG.request_cooldown_seconds,
            )
        )
        if retry_after > 0:
            await interaction.edit_original_response(
                content=f"Повторный запрос можно отправить через {math.ceil(retry_after)} сек.",
            )
            return

        self.last_request_at[author.id] = now
        await interaction.edit_original_response(
            content=(
                f"{admin_role.mention}, {author.mention} просит перенести его "
                f"в {admin_voice_channel.mention}."
            ),
            allowed_mentions=AllowedMentions(roles=[admin_role], users=[author]),
            view=AdminVoiceRequestView(author, admin_voice_channel),
        )


def setup(bot: Bot) -> None:
    bot.add_cog(AdminVoice(bot))
