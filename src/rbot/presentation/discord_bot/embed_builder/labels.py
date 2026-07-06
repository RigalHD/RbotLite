from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Final

from disnake import TextInputStyle, ui

from rbot.presentation.discord_bot.embed_builder.enums import EmbedField


@dataclass(frozen=True, slots=True)
class EmbedLabelSpec:
    field: EmbedField
    label: str
    placeholder: str
    max_length: int
    style: TextInputStyle = TextInputStyle.short

    def create(self) -> ui.Label:
        return ui.Label(
            self.label,
            ui.TextInput(
                custom_id=self.field.value,
                placeholder=self.placeholder,
                max_length=self.max_length,
                style=self.style,
            ),
        )


TITLE_LABEL: Final = EmbedLabelSpec(
    field=EmbedField.TITLE,
    label="Заголовок",
    placeholder="Заголовок",
    max_length=256,
)
DESCRIPTION_LABEL: Final = EmbedLabelSpec(
    field=EmbedField.DESCRIPTION,
    label="Текст",
    placeholder="Основной текст сообщения",
    max_length=4000,
    style=TextInputStyle.paragraph,
)
AUTHOR_LABEL: Final = EmbedLabelSpec(
    field=EmbedField.AUTHOR,
    label="Автор",
    placeholder="Подпись над заголовком",
    max_length=256,
)
FOOTER_LABEL: Final = EmbedLabelSpec(
    field=EmbedField.FOOTER,
    label="Футер",
    placeholder="Подпись внизу",
    max_length=2048,
)
IMAGE_URL_LABEL: Final = EmbedLabelSpec(
    field=EmbedField.IMAGE_URL,
    label="Ссылка на картинку",
    placeholder="https://example.com/image.png",
    max_length=2048,
)

EMBED_LABELS: Final[Mapping[EmbedField, EmbedLabelSpec]] = MappingProxyType(
    {
        spec.field: spec
        for spec in (
            TITLE_LABEL,
            DESCRIPTION_LABEL,
            AUTHOR_LABEL,
            FOOTER_LABEL,
            IMAGE_URL_LABEL,
        )
    },
)
