"""Парсер словаря IPA-исключений из текстового формата."""
from __future__ import annotations


def parse_dict(text: str) -> dict[str, str]:
    """
    Формат строки: 'word<TAB>IPA[/...]', '#' — комментарий.
    Срезает '/', берёт первый вариант из списка через ',', сохраняет первое вхождение.
    """
    result: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t", 1)
        if len(parts) != 2:
            continue
        word = parts[0].strip()
        ipa_val = parts[1].replace("/", "").split(",")[0].strip()
        if word not in result:
            result[word] = ipa_val
    return result