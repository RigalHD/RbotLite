from typing import Any

from disnake import (
    ButtonStyle,
    Embed,
    HTTPException,
    Member,
    TextChannel,
    TextInputStyle,
    ui,
)
from disnake.ext.commands import Bot
from disnake.interactions import MessageInteraction, ModalInteraction

from rbot.presentation.discord_bot.embed_builder.validation import validate_optional_url


class EmbedPublishView(ui.View):
    def __init__(self, author_id: int, channel: TextChannel, embed: Embed) -> None:
        super().__init__(timeout=300)
        self.author_id = author_id
        self.channel = channel
        self.embed = embed

    async def interaction_check(self, interaction: MessageInteraction[Bot]) -> bool:
        author = interaction.author
        if (
            author.id == self.author_id
            and isinstance(author, Member)
            and author.guild_permissions.administrator
        ):
            return True

        await interaction.response.send_message(
            "Управлять этим предпросмотром может только его автор.",
            ephemeral=True,
        )
        return False

    def disable_buttons(self) -> None:
        for item in self.children:
            if isinstance(item, ui.Button):
                item.disabled = True

    @ui.button(label="Опубликовать", style=ButtonStyle.green)
    async def publish(
        self,
        _button: ui.Button["EmbedPublishView"],
        interaction: MessageInteraction[Bot],
    ) -> None:
        guild = interaction.guild
        bot_member = guild.me if guild is not None else None
        if bot_member is None:
            await interaction.response.send_message(
                "Не удалось определить права бота на сервере.",
                ephemeral=True,
            )
            return

        permissions = self.channel.permissions_for(bot_member)
        if not permissions.send_messages or not permissions.embed_links:
            await interaction.response.send_message(
                "Боту нужны права «Отправлять сообщения» и «Встраивать ссылки» в выбранном канале.",
                ephemeral=True,
            )
            return

        await interaction.response.defer()
        try:
            message = await self.channel.send(embed=self.embed)
        except HTTPException:
            await interaction.followup.send(
                "Discord не принял embed. Проверьте ссылки и попробуйте снова.",
                ephemeral=True,
            )
            return

        self.disable_buttons()
        self.stop()
        await interaction.edit_original_response(
            content=f"Сообщение опубликовано: {message.jump_url}",
            embed=None,
            view=self,
        )

    @ui.button(label="Отмена", style=ButtonStyle.red)
    async def cancel(
        self,
        _button: ui.Button["EmbedPublishView"],
        interaction: MessageInteraction[Bot],
    ) -> None:
        self.disable_buttons()
        self.stop()
        await interaction.response.edit_message(
            content="Публикация отменена.",
            embed=None,
            view=self,
        )


class EmbedEditorModal(ui.Modal):
    def __init__(self, author_id: int, channel: TextChannel, color: int) -> None:
        self.author_id = author_id
        self.channel = channel
        self.color = color

        super().__init__(
            title="Редактор embed-сообщения",
            components=[
                ui.Label(
                    "Заголовок",
                    ui.TextInput(
                        custom_id="title",
                        placeholder="Необязательный заголовок",
                        required=False,
                        max_length=256,
                    ),
                ),
                ui.Label(
                    "Текст",
                    ui.TextInput(
                        custom_id="description",
                        style=TextInputStyle.paragraph,
                        placeholder="Основной текст сообщения",
                        max_length=4000,
                    ),
                ),
                ui.Label(
                    "Автор",
                    ui.TextInput(
                        custom_id="author",
                        placeholder="Необязательная подпись над заголовком",
                        required=False,
                        max_length=256,
                    ),
                ),
                ui.Label(
                    "Подвал",
                    ui.TextInput(
                        custom_id="footer",
                        placeholder="Необязательная подпись внизу",
                        required=False,
                        max_length=2048,
                    ),
                ),
                ui.Label(
                    "Ссылка на изображение",
                    ui.TextInput(
                        custom_id="image_url",
                        placeholder="https://example.com/image.png",
                        required=False,
                        max_length=2048,
                    ),
                ),
            ],
        )

    async def callback(self, interaction: ModalInteraction[Any]) -> None:
        values = interaction.text_values
        try:
            image_url = validate_optional_url(values["image_url"])
        except ValueError:
            await interaction.response.send_message(
                "Ссылка на изображение должна начинаться с http:// или https://.",
                ephemeral=True,
            )
            return

        embed = Embed(
            title=values["title"].strip() or None,
            description=values["description"].strip(),
            color=self.color,
        )
        if author := values["author"].strip():
            embed.set_author(name=author)
        if footer := values["footer"].strip():
            embed.set_footer(text=footer)
        if image_url is not None:
            embed.set_image(url=image_url)

        if len(embed) > 6000:
            await interaction.response.send_message(
                "Общий объём текста embed превышает лимит Discord в 6000 символов.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            content=f"Предпросмотр для {self.channel.mention}:",
            embed=embed,
            view=EmbedPublishView(self.author_id, self.channel, embed),
            ephemeral=True,
        )
