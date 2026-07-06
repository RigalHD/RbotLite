from enum import StrEnum


class EmbedColor(StrEnum):
    BLUE = "00A2FF"
    RED = "FF0000"
    GREEN = "135C19"
    YELLOW = "FFFF00"
    PURPLE = "8400FF"

    @property
    def label(self) -> str:
        labels = {
            self.BLUE: "Синий",
            self.RED: "Красный",
            self.GREEN: "Зелёный",
            self.YELLOW: "Жёлтый",
            self.PURPLE: "Фиолетовый",
        }
        return labels[self]

    @property
    def emoji(self) -> str:
        emojis = {
            self.BLUE: "🔵",
            self.RED: "🔴",
            self.GREEN: "🟢",
            self.YELLOW: "🟡",
            self.PURPLE: "🟣",
        }
        return emojis[self]

    def to_int(self) -> int:
        return int(self.value, 16)


class EmbedField(StrEnum):
    TITLE = "title"
    DESCRIPTION = "description"
    AUTHOR = "author"
    FOOTER = "footer"
    IMAGE_URL = "image_url"

    @property
    def label(self) -> str:
        labels = {
            self.TITLE: "Заголовок",
            self.DESCRIPTION: "Описание",
            self.AUTHOR: "Автор",
            self.FOOTER: "Футер",
            self.IMAGE_URL: "Картинка",
        }
        return labels[self]

    @property
    def selected_by_default(self) -> bool:
        return self in {self.TITLE, self.DESCRIPTION}
