from typing import Any

from disnake import (
    ButtonStyle,
    Embed,
    HTTPException,
    Member,
    SelectOption,
    TextChannel,
    ui,
)
from disnake.ext.commands import Bot
from disnake.interactions import MessageInteraction, ModalInteraction
from disnake.ui.select.string import StringSelect

from rbot.presentation.discord_bot.embed_builder.enums import EmbedColor, EmbedField
from rbot.presentation.discord_bot.embed_builder.labels import EMBED_LABELS
from rbot.presentation.discord_bot.embed_builder.validation import validate_optional_url


class EmbedColorSelect(StringSelect[ui.View]):
    def __init__(self, setup_view: "EmbedSetupView") -> None:
        self.setup_view = setup_view
        super().__init__(
            placeholder="Выберите готовый цвет",
            min_values=1,
            max_values=1,
            options=[
                SelectOption(label=color.label, value=color.value, emoji=color.emoji)
                for color in EmbedColor
            ],
        )

    async def callback(self, interaction: MessageInteraction[Any]) -> None:
        self.setup_view.color = EmbedColor(self.values[0]).to_int()
        await interaction.response.defer()


class EmbedFieldsSelect(StringSelect[ui.View]):
    def __init__(self, setup_view: "EmbedSetupView") -> None:
        self.setup_view = setup_view
        super().__init__(
            placeholder="Выберите содержимое",
            min_values=1,
            max_values=len(EmbedField),
            options=[
                SelectOption(
                    label=field.label,
                    value=field.value,
                    default=field.selected_by_default,
                )
                for field in EmbedField
            ],
        )

    async def callback(self, interaction: MessageInteraction[Any]) -> None:
        self.setup_view.fields = {EmbedField(value) for value in self.values}
        await interaction.response.defer()


class EmbedSetupView(ui.View):
    def __init__(self, author_id: int, channel: TextChannel, color: int) -> None:
        super().__init__(timeout=300)
        self.author_id = author_id
        self.channel = channel
        self.color = color
        self.fields = {EmbedField.TITLE, EmbedField.DESCRIPTION}
        self.add_item(EmbedColorSelect(self))
        self.add_item(EmbedFieldsSelect(self))

    async def interaction_check(self, interaction: MessageInteraction[Bot]) -> bool:
        author = interaction.author
        if (
            author.id == self.author_id
            and isinstance(author, Member)
            and author.guild_permissions.administrator
        ):
            return True

        await interaction.response.send_message(
            "Настраивать этот embed может только автор команды.",
            ephemeral=True,
        )
        return False

    def build_summary(self) -> str:
        return (
            f"Канал: {self.channel.mention}\n"
            "Выберите цвет и необходимые поля, затем нажмите «Открыть редактор»."
        )

    @ui.button(label="Открыть редактор", style=ButtonStyle.primary, row=2)
    async def open_editor(
        self,
        _button: ui.Button["EmbedSetupView"],
        interaction: MessageInteraction[Bot],
    ) -> None:
        await interaction.response.send_modal(
            EmbedEditorModal(
                self.author_id,
                self.channel,
                self.color,
                self.fields,
            ),
        )


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
    def __init__(
        self,
        author_id: int,
        channel: TextChannel,
        color: int,
        fields: set[EmbedField],
    ) -> None:
        self.author_id = author_id
        self.channel = channel
        self.color = color

        components = [EMBED_LABELS[field].create() for field in EmbedField if field in fields]

        super().__init__(
            title="Редактор embed-сообщения",
            components=components,
        )

    async def callback(self, interaction: ModalInteraction[Any]) -> None:
        await interaction.response.defer(ephemeral=True)

        values = interaction.text_values
        try:
            image_url = validate_optional_url(values.get(EmbedField.IMAGE_URL.value, ""))
        except ValueError:
            await interaction.edit_original_response(
                content="Ссылка на картинку должна начинаться с http:// или https://.",
            )
            return

        embed = Embed(
            title=values.get(EmbedField.TITLE.value),
            description=values.get(EmbedField.DESCRIPTION.value),
            color=self.color,
        )
        if author := values.get(EmbedField.AUTHOR.value):
            embed.set_author(name=author)
        if footer := values.get(EmbedField.FOOTER.value):
            embed.set_footer(text=footer)
        if image_url is not None:
            embed.set_image(url=image_url)

        if len(embed) > 6000:
            await interaction.edit_original_response(
                content="Общий объём текста embed превышает лимит Discord в 6000 символов.",
            )
            return

        await interaction.edit_original_response(
            content=f"Предпросмотр для {self.channel.mention}:",
            embed=embed,
            view=EmbedPublishView(self.author_id, self.channel, embed),
        )
