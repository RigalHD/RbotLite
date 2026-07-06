from urllib.parse import urlparse


def parse_color(value: str) -> int:
    normalized = value.strip().lower().removeprefix("#").removeprefix("0x")
    if len(normalized) != 6:
        raise ValueError

    color = int(normalized, 16)
    if not 0 <= color <= 0xFFFFFF:
        raise ValueError

    return color


def validate_optional_url(value: str) -> str | None:
    value = value.strip()
    if not value:
        return None

    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError

    return value
