from typing import Any

from disnake import (
    ButtonStyle,
    Embed,
    HTTPException,
    Member,
    SelectOption,
    TextChannel,
    TextInputStyle,
    ui,
)
from disnake.ext.commands import Bot
from disnake.interactions import MessageInteraction, ModalInteraction
from disnake.ui.select.string import StringSelect

from rbot.presentation.discord_bot.embed_builder.validation import validate_optional_url

EMBED_FIELD_LABELS = {
    "title": "заголовок",
    "description": "описание",
    "author": "автор",
    "footer": "подвал",
    "image_url": "изображение",
}


class EmbedColorSelect(StringSelect[ui.View]):
    def __init__(self, setup_view: "EmbedSetupView") -> None:
        self.setup_view = setup_view
        super().__init__(
            placeholder="Выберите готовый цвет",
            min_values=1,
            max_values=1,
            options=[
                SelectOption(label="Синий", value="00A2FF", emoji="🔵"),
                SelectOption(label="Красный", value="FF0000", emoji="🔴"),
                SelectOption(label="Зелёный", value="135C19", emoji="🟢"),
                SelectOption(label="Жёлтый", value="FFFF00", emoji="🟡"),
                SelectOption(label="Фиолетовый", value="8400FF", emoji="🟣"),
            ],
        )

    async def callback(self, interaction: MessageInteraction[Any]) -> None:
        self.setup_view.color = int(self.values[0], 16)
        await interaction.response.edit_message(
            content=self.setup_view.build_summary(),
            view=self.setup_view,
        )


class EmbedFieldsSelect(StringSelect[ui.View]):
    def __init__(self, setup_view: "EmbedSetupView") -> None:
        self.setup_view = setup_view
        super().__init__(
            placeholder="Выберите содержимое embed",
            min_values=1,
            max_values=len(EMBED_FIELD_LABELS),
            options=[
                SelectOption(label="Заголовок", value="title", default=True),
                SelectOption(label="Описание", value="description", default=True),
                SelectOption(label="Автор", value="author"),
                SelectOption(label="Подвал", value="footer"),
                SelectOption(label="Изображение", value="image_url"),
            ],
        )

    async def callback(self, interaction: MessageInteraction[Any]) -> None:
        self.setup_view.fields = set(self.values)
        await interaction.response.edit_message(
            content=self.setup_view.build_summary(),
            view=self.setup_view,
        )


class EmbedSetupView(ui.View):
    def __init__(self, author_id: int, channel: TextChannel, color: int) -> None:
        super().__init__(timeout=300)
        self.author_id = author_id
        self.channel = channel
        self.color = color
        self.fields = {"title", "description"}
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
        fields = ", ".join(
            EMBED_FIELD_LABELS[field]
            for field in EMBED_FIELD_LABELS
            if field in self.fields
        )
        return (
            f"Канал: {self.channel.mention}\n"
            f"Цвет: `#{self.color:06X}`\n"
            f"Поля: {fields}\n\n"
            "Настройте параметры и нажмите «Открыть редактор»."
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
        fields: set[str],
    ) -> None:
        self.author_id = author_id
        self.channel = channel
        self.color = color

        components: list[ui.Label] = []
        if "title" in fields:
            components.append(
                ui.Label(
                    "Заголовок",
                    ui.TextInput(
                        custom_id="title",
                        placeholder="Заголовок embed",
                        max_length=256,
                    ),
                ),
            )
        if "description" in fields:
            components.append(
                ui.Label(
                    "Текст",
                    ui.TextInput(
                        custom_id="description",
                        style=TextInputStyle.paragraph,
                        placeholder="Основной текст сообщения",
                        max_length=4000,
                    ),
                ),
            )
        if "author" in fields:
            components.append(
                ui.Label(
                    "Автор",
                    ui.TextInput(
                        custom_id="author",
                        placeholder="Подпись над заголовком",
                        max_length=256,
                    ),
                ),
            )
        if "footer" in fields:
            components.append(
                ui.Label(
                    "Подвал",
                    ui.TextInput(
                        custom_id="footer",
                        placeholder="Подпись внизу",
                        max_length=2048,
                    ),
                ),
            )
        if "image_url" in fields:
            components.append(
                ui.Label(
                    "Ссылка на изображение",
                    ui.TextInput(
                        custom_id="image_url",
                        placeholder="https://example.com/image.png",
                        max_length=2048,
                    ),
                ),
            )

        super().__init__(
            title="Редактор embed-сообщения",
            components=components,
        )

    async def callback(self, interaction: ModalInteraction[Any]) -> None:
        values = interaction.text_values
        try:
            image_url = validate_optional_url(values.get("image_url", ""))
        except ValueError:
            await interaction.response.send_message(
                "Ссылка на изображение должна начинаться с http:// или https://.",
                ephemeral=True,
            )
            return

        embed = Embed(
            title=values.get("title"),
            description=values.get("description"),
            color=self.color,
        )
        if author := values.get("author"):
            embed.set_author(name=author)
        if footer := values.get("footer"):
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
