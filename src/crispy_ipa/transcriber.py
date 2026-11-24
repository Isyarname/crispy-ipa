"""Класс-оркестратор транскрипции."""
from __future__ import annotations

from importlib import resources

from .conversion import to_ipa
from . import eng_to_ipa_rules
from .dict_parser import parse_dict
from .dsl_parser import parse_rules
from .rule_engine import CompiledRule

_EN_DICT_NAME = "en_dict.txt"

# Всё грузится при импорте модуля.
_RULES: tuple[CompiledRule, ...] = tuple(
    parse_rules(eng_to_ipa_rules.rules, eng_to_ipa_rules.macros)
)
_DICT: dict[str, str] = parse_dict(
    resources.files("crispy_ipa.data").joinpath(_EN_DICT_NAME).read_text(encoding="utf-8")
)

def _normalize_vocabulary(vocabulary: dict[str, str] | None) -> dict[str, str]:
    result = dict(vocabulary or {})
    for k, v in list(result.items()):
        if k != k.lower():
            result.setdefault(k.lower(), v)
    return result


class Transcriber:
    def __init__(self, custom_vocabulary: dict[str, str] | None = None) -> None:
        self._merged_vocabulary = dict(_DICT)
        self._merged_vocabulary.update(_normalize_vocabulary(custom_vocabulary))
        self._long_keys = frozenset(k for k in self._merged_vocabulary if len(k) >= 4)

    def transcribe(self, text: str) -> str:
        return to_ipa(text, self._merged_vocabulary, self._long_keys, _RULES)

    def __repr__(self) -> str:
        return (
            f"Transcriber(eng_to_ipa_rules={len(_RULES)}, "
            f"dict={len(self._merged_vocabulary)})"
        )
