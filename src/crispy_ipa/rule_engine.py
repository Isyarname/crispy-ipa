"""Движок применения скомпилированных фонологических правил к тексту."""
import re
import unicodedata

Step = tuple[bool, tuple[str, ...]]
CompiledRule = tuple[str, str, tuple[Step, ...], tuple[Step, ...]]

WORD_RE = re.compile(r"([^\W\d_]+)")


def check_right(text: str, pos: int, steps: tuple[Step, ...]) -> bool:
    """Проверяет контекст справа от найденного паттерна."""
    for i, (is_neg, variants) in enumerate(steps):
        if is_neg:
            if text.startswith(variants, pos):
                return False
            rest = steps[i + 1 :]
            if not rest:
                return True
            # Если после отрицания есть ещё шаги, пробуем сдвиг от 1 до max_len
            max_skip = max(len(v) for v in variants)
            for skip in range(1, max_skip + 1):
                if pos + skip <= len(text) and check_right(text, pos + skip, rest):
                    return True
            return False
        else:
            val = variants
            if not text.startswith(val, pos):
                return False
            pos += len(val)
    return True


def check_left(text: str, pos: int, steps: tuple[Step, ...]) -> bool:
    """Проверяет контекст слева от найденного паттерна (в обратном направлении)."""
    for i in range(len(steps) - 1, -1, -1):
        is_neg, variants = steps[i]
        if is_neg:
            if text.endswith(variants, 0, pos):
                return False
            rest = steps[:i]
            if not rest:
                return True
            max_skip = max(len(v) for v in variants)
            for skip in range(1, max_skip + 1):
                if pos - skip >= 0 and check_left(text, pos - skip, rest):
                    return True
            return False
        else:
            val = variants
            if not text.endswith(val, 0, pos):
                return False
            pos -= len(val)
    return True


def apply_rules(text: str, rules: list[CompiledRule] | tuple[CompiledRule, ...]) -> str:
    # Обрамляем каждое слово символом границы слова '#'
    text = WORD_RE.sub(r"#\1#", text)

    for L, R, left_steps, right_steps in rules:
        if L not in text:
            continue

        if not left_steps and not right_steps:
            text = text.replace(L, R)
            continue

        pat_len = len(L)
        indexes = []
        index = text.find(L)
        while index != -1:
            if check_left(text, index, left_steps) and check_right(text, index + pat_len, right_steps):
                indexes.append(index)
            index = text.find(L, index + pat_len)

        for idx in reversed(indexes):
            text = text[:idx] + R + text[idx + pat_len:]

    return text.replace("#", "")


def process_text(text: str, rules: list[CompiledRule] | tuple[CompiledRule, ...]) -> str:
    return unicodedata.normalize("NFC", apply_rules(text, rules))
