import re

def with_spaces(sep: str) -> str:
    return rf"\s*{re.escape(sep)}\s*"
token = r"(\S+)"
RULE_PATTERN = re.compile(
    token + with_spaces("->") + token + rf"(?:{with_spaces('/')}{token})?"
)

def parse(rules_str: str) -> list:
    prepared_rules = []
    for line in rules_str.strip().splitlines():
        prepared_rules.extend(RULE_PATTERN.findall(line))
    return prepared_rules

def prepare_macros(macros: dict[str, str]) -> list[tuple[str, str]]:
    """
    Возвращает готовый отсортированнный по убыванию длины ключа список пар (old, new),
    пригодный для expand_macros.
    """
    items = list(macros.items())
    items.sort(key=lambda e: -len(e[0]))
    return items

def expand_macros(rules: str, prepared_macros: list[tuple[str, str]]) -> str:
    """Подставляет уже подготовленные макросы в одно правило."""
    for old, new in prepared_macros:
        rules = rules.replace(old, new)
    return rules

def build_rules(rules_str: str, macros: dict[str, str] | None = None) -> list:
    """
    🌟 ГЛАВНАЯ ЧИСТАЯ ФУНКЦИЯ МОДУЛЯ.
    Принимает сырую строку правил и словарь макросов.
    Возвращает готовый плоский список кортежей замен.
    """
    if macros:
        rules_str = expand_macros(rules_str, prepare_macros(macros))

    return parse(rules_str)
