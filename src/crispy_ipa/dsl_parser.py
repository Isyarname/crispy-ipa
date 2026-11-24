"""Препроцессор макросов и парсер фонологических правил DSL."""
import itertools
import re

Step = tuple[bool, tuple[str, ...]]
CompiledRule = tuple[str, str, tuple[Step, ...], tuple[Step, ...]]


def with_spaces(sep: str) -> str:
    return rf"\s*{re.escape(sep)}\s*"


token = r"(\S+)"
RULE_PATTERN = re.compile(
    token + with_spaces("->") + token + rf"(?:{with_spaces('/')}{token})?"
)
BRACKETS_RE = re.compile(r"\[(.*?)\]")
GROUP_RE = re.compile(r"\(([^)]*)\)")
CONTEXT_TOKEN_RE = re.compile(r"!?\[[^\]]+\]|!?\([^\)]+\)|!?.")
NEG_GROUP_RE = re.compile(r"!\(([^)]+)\)|([^\s!]+)")


def parse_lines(rules_str: str) -> list[tuple[str, str, str]]:
    prepared_rules = []
    for line in rules_str.strip().splitlines():
        prepared_rules.extend(RULE_PATTERN.findall(line))
    return prepared_rules


def prepare_macros(macros: dict[str, str]) -> list[tuple[str, str]]:
    """
    Возвращает отсортированный по убыванию длины ключа список пар (old, new),
    пригодный для expand_macros.
    """
    items = list(macros.items())
    items.sort(key=lambda e: -len(e))
    return items


def expand_macros(rules: str, prepared_macros: list[tuple[str, str]]) -> str:
    """Подставляет подготовленные макросы в текст правил."""
    for old, new in prepared_macros:
        rules = rules.replace(old, new)
    return rules


def replace_brackets(text: str) -> str:
    for c in BRACKETS_RE.findall(text):
        text = text.replace(f"[{c}]", f"({'|'.join(c)})")
    return text


def expand_pair(left: str, right: str) -> list[tuple[str, str]]:
    """Раскрывает скобки [...] и (...) с сохранением попарного соответствия L -> R."""
    rule1 = replace_brackets(left)
    rule2 = replace_brackets(right)

    if "(" not in rule2:
        matches1 = GROUP_RE.findall(rule1)
        if len(matches1) == 1:
            rule2 = f"({rule2})"

    parts1 = GROUP_RE.split(rule1)
    parts2 = GROUP_RE.split(rule2)
    if len(parts1) != len(parts2):
        raise ValueError(f"Строки имеют разное количество скобочных групп: {left} -> {right}")

    aligned1 = []
    aligned2 = []
    for i in range(len(parts1)):
        if i % 2 == 0:
            aligned1.append([parts1[i]])
            aligned2.append([parts2[i]])
        else:
            opts1 = parts1[i].split("|")
            opts2 = parts2[i].split("|")
            if len(opts2) <= 1 and len(opts1) > 1:
                opts2 = opts2 * len(opts1)
            elif len(opts1) != len(opts2):
                raise ValueError(
                    f"Невозможно сопоставить варианты в группе {i // 2 + 1}: {left} -> {right}"
                )
            aligned1.append(opts1)
            aligned2.append(opts2)

    combs1 = itertools.product(*aligned1)
    combs2 = itertools.product(*aligned2)
    return [("".join(c1), "".join(c2)) for c1, c2 in zip(combs1, combs2)]

def normalize_negated(tok: str) -> str:
    """Превращает '![aei]' -> '!(a|e|i)', '!a' -> '!(a)', '!(a|b)' -> '!(a|b)'."""
    body = tok[1:]
    if body.startswith("[") and body.endswith("]"):
        return f"!({'|'.join(body[1:-1])})"
    if body.startswith("(") and body.endswith(")"):
        return f"!{body}"
    return f"!({body})"


def expand_context(context: str) -> list[str]:
    """
    Раскрывает положительные группы в контексте через product,
    а отрицания приводит к единому виду '!(a|b|c)'.
    """
    if not context:
        return [""]

    parts: list[list[str]] = []
    for tok in CONTEXT_TOKEN_RE.findall(context):
        if tok.startswith("!"):
            parts.append([normalize_negated(tok)])
        elif tok.startswith("[") and tok.endswith("]"):
            parts.append(list(tok[1:-1]))
        elif tok.startswith("(") and tok.endswith(")"):
            parts.append(tok[1:-1].split("|"))
        else:
            parts.append([tok])

    return ["".join(comb) for comb in itertools.product(*parts)]


def compile_context(context: str) -> tuple[tuple[Step, ...], tuple[Step, ...]]:
    """Разбирает '_ac!(v)' в ((), ((False, ('ac',)), (True, ('v',))))."""
    if not context:
        return (), ()
    if context.count("_") != 1:
        raise ValueError(f"В контексте должен быть ровно один символ '_': {context}")

    left_raw, right_raw = context.split("_")

    def parse_side(side: str) -> tuple[Step, ...]:
        steps = []
        for neg_body, plain in NEG_GROUP_RE.findall(side):
            if neg_body:
                steps.append((True, tuple(neg_body.split("|"))))
            else:
                steps.append((False, (plain,)))
        return tuple(steps)

    return parse_side(left_raw), parse_side(right_raw)


def parse_rules(
    rules_str: str,
    macros: dict[str, str] | None = None,
) -> list[CompiledRule]:
    """
    Главная чистая функция парсера.
    Раскрывает макросы, парсит синтаксис L -> R / C и разворачивает скобки в L, R и C.
    Возвращает плоский список кортежей (left, right, left_steps, right_steps).
    """
    if macros:
        rules_str = expand_macros(rules_str, prepare_macros(macros))

    result = []
    for left, right, context in parse_lines(rules_str):
        expanded_pairs = expand_pair(left, right)
        compiled_contexts = [compile_context(ctx) for ctx in expand_context(context)]
        for exp_left, exp_right in expanded_pairs:
            # Нормализуем символ удаления звука ∅ в пустую строку
            clean_right = "" if exp_right in ("∅", "_") else exp_right
            for left_steps, right_steps in compiled_contexts:
                result.append((exp_left, clean_right, left_steps, right_steps))

    result.sort(key=lambda r: (-len(r), not (r or r)))
    return result
