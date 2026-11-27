"""Гибридный движок транскрипции: словарь исключений + rule_engine."""
from __future__ import annotations

import os
import re
from collections.abc import Sequence
from functools import lru_cache
from . import rule_engine
from .rule_engine import CompiledRule

_WORD_PATTERN = re.compile(r"^[a-zA-Z']+$")
_TOKEN_PATTERN = re.compile(r"[a-zA-Z']+|[^a-zA-Z']+")

# Регулярки для умного разбиения и нормализации регистра
_CAMEL_BOUNDARY = re.compile(r'(?<=[a-z])(?=[A-Z])')
_ABBR_WORD_BOUNDARY = re.compile(r'(?<=[A-Z])(?=[A-Z][a-z])')
_UPPER_SEQUENCE = re.compile(r'(?<=[A-Z])(?=[A-Z])')
_WORD_START = re.compile(r'([A-Z])(?=[a-z])')

_SUFFIXES = sorted({
    "ization", "isation",
    "izing", "ising",
    "izer", "iser",
    "ment", "ness", "tion", "sion", "able", "ible",
    "ful", "less", "ous", "ive",
    "ing", "ed", "ly", "er", "or", "est",
    "es", "s", "'s",
}, key=len, reverse=True)

MAX_DICT_WORD_LEN = 8
_MIN_PREFIX_WORD_LEN = 4

# (текст_сегмента, из_словаря, контекст_слева)
Segment = tuple[str, bool, str]
UnknownItem = tuple[str, str]


# ─────────────────────────── Токенизация ───────────────────────────

def smart_lower(text: str) -> str:
    text = _CAMEL_BOUNDARY.sub('-', text)
    text = _ABBR_WORD_BOUNDARY.sub('-', text)
    text = _UPPER_SEQUENCE.sub('-', text)
    text = _WORD_START.sub(lambda m: m.group(1).lower(), text)
    return text


def _tokenize(text: str) -> list[str]:
    return _TOKEN_PATTERN.findall(text)


def _is_word_token(token: str) -> bool:
    return bool(_WORD_PATTERN.match(token))


def _is_abbreviation(token: str) -> bool:
    return len(token) >= 2 and token.isupper()


# ─────────────────────────── Суффиксы и разбиение ───────────────────────────

def _find_suffix(word_lower: str) -> tuple[int, str] | None:
    for suffix in _SUFFIXES:
        if word_lower.endswith(suffix) and len(word_lower) > len(suffix):
            return (len(word_lower) - len(suffix), suffix)
    return None


def _ends_with_dict_word(
    segments: list[tuple[str, bool]],
    min_len: int = _MIN_PREFIX_WORD_LEN,
) -> bool:
    if not segments:
        return False
    last_text, is_dict = segments[-1]
    return is_dict and len(last_text) >= min_len


def _split_word_from_end(
    word: str,
    word_lower: str,
    boundary: int,
    long_keys: frozenset[str],
) -> list[tuple[str, bool]]:
    if not long_keys:
        return [(word[:boundary], False)]

    segments: list[tuple[str, bool]] = []
    pos = boundary

    while pos > 0:
        best_match = None
        max_len = min(pos, MAX_DICT_WORD_LEN)
        for length in range(max_len, 3, -1):
            start = pos - length
            candidate = word_lower[start:pos]
            if candidate in long_keys:
                best_match = (start, pos)
                break

        if best_match:
            start, end = best_match
            segments.append((word[start:end], True))
            pos = start
        else:
            pos -= 1
            if segments and not segments[-1][1]:
                segments[-1] = (word[pos] + segments[-1][0], False)
            else:
                segments.append((word[pos], False))

    segments.reverse()
    return segments


@lru_cache(maxsize=10000)
def _split_word_cached(
    word: str,
    word_lower: str,
    boundary: int,
    long_keys: frozenset[str],
) -> tuple[tuple[str, bool], ...]:
    return tuple(_split_word_from_end(word, word_lower, boundary, long_keys))


def _attach_left_context(raw_segments: list[tuple[str, bool]]) -> list[Segment]:
    """Прикрепляет последние 4 графемы словарной основы к следующему за ней суффиксу."""
    result: list[Segment] = []
    for i, (seg_text, is_dict) in enumerate(raw_segments):
        if not is_dict and i > 0 and raw_segments[i - 1][1]:
            prev_tail = raw_segments[i - 1][0][-4:].lower()
            result.append((seg_text, False, prev_tail))
        else:
            result.append((seg_text, is_dict, ""))
    return result


# ─────────────────────────── Шаг 1: Разбиение токенов на сегменты ───────────────────────────

def _build_word_segments(
    tokens: list[str],
    custom_exceptions: dict[str, str],
    long_keys: frozenset[str],
) -> dict[str, list[Segment]]:
    word_segments: dict[str, list[Segment]] = {}

    for token in tokens:
        if not _is_word_token(token):
            continue

        word_lower = token.lower()
        if word_lower in word_segments:
            continue

        if _is_abbreviation(token):
            word_segments[word_lower] = [(token, False, "")]
            continue

        if word_lower in custom_exceptions:
            word_segments[word_lower] = [(token, True, "")]
            continue

        suffix_result = _find_suffix(word_lower)
        if suffix_result:
            boundary, suffix = suffix_result
            prefix_segments = list(
                _split_word_cached(token, word_lower, boundary, long_keys)
            )
            if _ends_with_dict_word(prefix_segments):
                raw_segments = prefix_segments + [(suffix, False)]
            else:
                raw_segments = list(
                    _split_word_cached(token, word_lower, len(word_lower), long_keys)
                )
        else:
            raw_segments = list(
                _split_word_cached(token, word_lower, len(word_lower), long_keys)
            )

        word_segments[word_lower] = _attach_left_context(raw_segments)

    return word_segments


# ─────────────────────────── Шаг 2: Сбор неизвестных слов ───────────────────────────

def _collect_unknown_words(
    word_segments: dict[str, list[Segment]],
) -> list[UnknownItem]:
    unknown: list[UnknownItem] = []
    seen: set[UnknownItem] = set()

    for segments in word_segments.values():
        for seg_text, is_dict, prev_tail in segments:
            if not is_dict:
                item = (seg_text, prev_tail)
                if item not in seen:
                    unknown.append(item)
                    seen.add(item)

    return unknown


# ─────────────────────────── Шаг 3: Транскрипция неизвестных слов ───────────────────────────

def _transcribe_suffix(
    stem_tail: str,
    suffix: str,
    rules_tuple: tuple[CompiledRule, ...],
) -> str:
    """Транскрибирует графемный суффикс с опорой на последние 4 графемы основы."""
    full_ipa = rule_engine.transcribe(stem_tail + suffix, rules_tuple)
    tail_ipa = rule_engine.transcribe(stem_tail, rules_tuple)
    common_len = len(os.path.commonprefix([full_ipa, tail_ipa]))
    return full_ipa[common_len:]


def _bulk_transcribe(
    unknown_items: list[UnknownItem],
    transcription_rules: Sequence[CompiledRule],
) -> dict[UnknownItem, str]:
    if not unknown_items:
        return {}

    rules_tuple = (
        transcription_rules
        if isinstance(transcription_rules, tuple)
        else tuple(transcription_rules)
    )

    mapping: dict[UnknownItem, str] = {}
    for seg_text, prev_tail in unknown_items:
        if prev_tail:
            mapping[(seg_text, prev_tail)] = _transcribe_suffix(
                prev_tail, seg_text.lower(), rules_tuple
            )
        else:
            mapping[(seg_text, prev_tail)] = rule_engine.transcribe(
                seg_text, rules_tuple
            )
    return mapping


# ─────────────────────────── Шаг 4: Сборка результата ───────────────────────────

def _build_final_tokens(
    tokens: list[str],
    word_segments: dict[str, list[Segment]],
    custom_exceptions: dict[str, str],
    english_mapping: dict[UnknownItem, str],
) -> list[str]:
    final_tokens: list[str] = []

    for token in tokens:
        if not _is_word_token(token):
            final_tokens.append(token)
            continue

        word_lower = token.lower()
        segments = word_segments[word_lower]
        ipa_parts: list[str] = []

        for seg_text, is_dict, prev_tail in segments:
            if is_dict:
                ipa_parts.append(custom_exceptions[seg_text.lower()])
            else:
                ipa_parts.append(
                    english_mapping.get((seg_text, prev_tail), seg_text)
                )

        final_tokens.append("".join(ipa_parts))

    return final_tokens


# ─────────────────────────── Шаг 5: Нормализация ───────────────────────────
VOWELS = "aæɑɒɔəɚɛɜɪiʊuʌeo"


def normalize(text: str) -> str:
    for v in VOWELS:
        text = text.replace(f"ɝ{v}", f"ɜɹ{v}")
    return text


# ─────────────────────────── Главная функция ───────────────────────────

def to_ipa(
    text: str,
    custom_exceptions: dict[str, str],
    long_keys: frozenset[str] | None,
    transcription_rules: Sequence[CompiledRule],
) -> str:
    if not text:
        return ""

    text = smart_lower(text)
    tokens = _tokenize(text)
    if not tokens:
        return ""

    if long_keys is None:
        long_keys = frozenset(k for k in custom_exceptions if len(k) >= 4)

    word_segments = _build_word_segments(tokens, custom_exceptions, long_keys)
    unknown_words = _collect_unknown_words(word_segments)
    english_mapping = _bulk_transcribe(unknown_words, transcription_rules)
    final_tokens = _build_final_tokens(
        tokens, word_segments, custom_exceptions, english_mapping
    )

    return normalize("".join(final_tokens).strip())


def clear_split_cache() -> None:
    _split_word_cached.cache_clear()
    rule_engine.clear_cache()
