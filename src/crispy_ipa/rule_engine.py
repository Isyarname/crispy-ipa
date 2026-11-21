"""Сверхбыстрый движок параллельного неразрушающего применения фонологических правил."""
import functools
import unicodedata

Step = tuple[bool, tuple[str, ...]]
CompiledRule = tuple[str, str, tuple[Step, ...], tuple[Step, ...]]


def check_right(text: str, pos: int, steps: tuple[Step, ...]) -> bool:
    for i, (is_neg, variants) in enumerate(steps):
        if is_neg:
            if text.startswith(variants, pos):
                return False
            rest = steps[i + 1 :]
            if not rest:
                return True
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

@functools.lru_cache(maxsize=8)
def _index_rules(
    rules: tuple[CompiledRule, ...],
) -> dict[str, tuple[tuple[int, CompiledRule], ...]]:
    """Группирует правила по первому символу L с сохранением их индекса приоритета."""
    buckets: dict[str, list[tuple[int, CompiledRule]]] = {}
    for idx, rule in enumerate(rules):
        first_char = rule[0][0]
        buckets.setdefault(first_char, []).append((idx, rule))
    return {ch: tuple(r_list) for ch, r_list in buckets.items()}


def apply_rules(word: str, rules: tuple[CompiledRule, ...]) -> str:
    if not word:
        return word

    src = f"#{word}#"
    src_len = len(src)
    free_chars = src_len - 2
    occupied = [False] * src_len
    edits: list[tuple[int, int, str]] = []

    buckets = _index_rules(rules)

    # <-- ВОТ СЮДА ВСТАВЛЯЕТСЯ ЭТОТ БЛОК -->
    candidate_rules: list[tuple[int, CompiledRule]] = []
    for ch in dict.fromkeys(word):
        if ch in buckets:
            candidate_rules.extend(buckets[ch])
    candidate_rules.sort()

    for _, (L, R, left_steps, right_steps) in candidate_rules:
        if L not in src:
            continue

        pat_len = len(L)
        index = src.find(L, 1)
        while index != -1:
            end = index + pat_len
            if not any(occupied[index:end]):
                if check_left(src, index, left_steps) and check_right(src, end, right_steps):
                    edits.append((index, end, R))
                    for i in range(index, end):
                        occupied[i] = True
                    free_chars -= pat_len
                    if free_chars <= 0:
                        break
            index = src.find(L, end)

        if free_chars <= 0:
            break

    if not edits:
        return word

    edits.sort(key=lambda e: e[0])

    parts: list[str] = []
    last_pos = 1
    for start, end, replacement in edits:
        parts.append(src[last_pos:start])
        parts.append(replacement)
        last_pos = end
    parts.append(src[last_pos:-1])

    return "".join(parts)


def process_text(text: str, rules: list[CompiledRule] | tuple[CompiledRule, ...]) -> str:
    rules_tuple = rules if isinstance(rules, tuple) else tuple(rules)
    return unicodedata.normalize("NFC", apply_rules(text, rules_tuple))
