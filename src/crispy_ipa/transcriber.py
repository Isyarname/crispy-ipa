"""Класс-оркестратор транскрипции."""
from __future__ import annotations

import pickle
from importlib import resources
from pathlib import Path
from . import eng_to_ipa_hybrid
from .rule_engine import CompiledRule

_PACKAGE_DATA = resources.files("crispy_ipa.data")

# Пути к скомпилированным данным внутри пакета
_ENG_TO_IPA_RULES_PATH = Path(str(_PACKAGE_DATA.joinpath("eng_to_ipa_rules.pkl")))
_EN_DICT_PATH = Path(str(_PACKAGE_DATA.joinpath("en_dict.pkl")))


class Transcriber:

    def __init__(
        self,
        custom_vocabulary: dict[str, str] | None = None,
    ) -> None:
        """
        Args:
            custom_vocabulary: Пользовательский словарь (дополняет встроенный).
        """
        # --- Пользовательский словарь (сохраняем оригинал + вариант в нижнем регистре) ---
        self._custom_vocabulary: dict[str, str] = {}
        if custom_vocabulary:
            for k, v in custom_vocabulary.items():
                self._custom_vocabulary[k] = v
                k_lower = k.lower()
                if k_lower not in custom_vocabulary:
                    self._custom_vocabulary[k_lower] = v


        # --- Загрузка ресурсов ---
        self._eng_to_ipa_rules: tuple[CompiledRule, ...] = tuple(
            self._load_pickle(_ENG_TO_IPA_RULES_PATH)
        )
        self._en_dict: dict[str, str] = self._load_pickle(_EN_DICT_PATH)

        # --- Объединённый словарь (собирается один раз) ---
        if self._custom_vocabulary:
            self._merged_vocabulary = {**self._en_dict, **self._custom_vocabulary}
        else:
            self._merged_vocabulary = self._en_dict

        # --- Ключи длиной ≥ 4 для разбиения незнакомых слов ---
        self._long_keys = frozenset(
            k for k in self._merged_vocabulary if len(k) >= 4
        )

    # ─────────────────────────── Публичный API ───────────────────────────

    def transcribe(self, text: str) -> str:
        return eng_to_ipa_hybrid.transcribe(
            text,
            self._merged_vocabulary,
            self._long_keys,
            self._eng_to_ipa_rules,
        )

    # ─────────────────────────── Доступ к ресурсам ───────────────────────

    def get_eng_to_ipa_rules(self) -> tuple[CompiledRule, ...]:
        """Возвращает скомпилированные правила English → IPA."""
        return self._eng_to_ipa_rules

    # ─────────────────────────── Внутренние методы ───────────────────────

    @staticmethod
    def _load_pickle(path: Path):
        if not path.exists():
            raise FileNotFoundError(f"Файл не найден: {path}")
        with open(path, "rb") as f:
            return pickle.load(f)

    # ─────────────────────────── Магические методы ────────────────────────

    def __repr__(self) -> str:
        return (
            f"Transcriber("
            f"eng_to_ipa_rules={len(self._eng_to_ipa_rules)}, "
            f"dict={len(self._merged_vocabulary)})"
        )
