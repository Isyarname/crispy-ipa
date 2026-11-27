"""Чистка en_dict.txt: аудит + безопасная нормализация. Без регулярок, идемпотентно.

    py scripts/clean_dict.py           # сухой прогон: только отчёт
    py scripts/clean_dict.py --write   # применить и перезаписать файл
"""
import sys
from pathlib import Path

DICT = Path(__file__).resolve().parents[1] / "src" / "crispy_ipa" / "data" / "en_dict.txt"

VOWELS = "aeiouyɑɔæɛɜəɪʊʌɐɚɝ"
BAD_IPA = set("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZq")


def split_variants(field):
    out = []
    for part in field.split(","):
        part = part.strip()
        if part.startswith("/"):
            part = part[1:]
        if part.endswith("/"):
            part = part[:-1]
        part = part.strip()
        if part:
            out.append(part)
    return out


def normalize_thought(variants):
    first = variants[0]
    if "ɑ" not in first or "ɔ" in first:
        return variants
    target = first.replace("ɑ", "ɔ")
    for i, v in enumerate(variants[1:], 1):
        if v == target:
            return [v] + variants[:i] + variants[i + 1:]
    return variants


def dedup(variants):
    seen, out = set(), []
    for v in variants:
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out


def main():
    write = "--write" in sys.argv
    if not DICT.exists():
        raise SystemExit(f"не найден: {DICT}")
    lines = DICT.read_text(encoding="utf-8").splitlines()

    seen_words = set()
    out = []
    stats = {"dup": 0, "malformed": 0, "multiword": 0, "case": 0,
             "thought": 0, "dedup_var": 0, "suspicious": 0, "no_vowel": 0}
    examples = {k: [] for k in stats}

    def note(cat, line):
        stats[cat] += 1
        if len(examples[cat]) < 8:
            examples[cat].append(line)

    for line in lines:
        s = line.strip()
        if not s or s.startswith("#"):
            out.append(line)
            continue
        if "\t" not in line:
            note("malformed", line)
            continue
        word, field = line.split("\t", 1)
        word = word.strip()
        variants = split_variants(field)
        if not word or not variants:
            note("malformed", line)
            continue
        if " " in word:
            note("multiword", line)
            continue

        low = word.lower()
        if low != word:
            note("case", line)
        if low in seen_words:
            note("dup", line)
            continue
        seen_words.add(low)

        if any(ch in BAD_IPA for v in variants for ch in v):
            note("suspicious", line)
        if not any(ch in VOWELS for ch in variants[0]):
            note("no_vowel", line)

        new = normalize_thought(variants)
        if new != variants:
            note("thought", line)
        new2 = dedup(new)
        if new2 != new:
            note("dedup_var", line)

        out.append(low + "\t" + ", ".join("/" + v + "/" for v in new2))

    print(f"файл:            {DICT}")
    print(f"строк на входе:  {len(lines)}")
    print(f"строк на выходе: {len(out)}")
    for cat, n in stats.items():
        print(f"  {cat:12} {n}")
        for ex in examples[cat]:
            print(f"      {ex}")
    if write:
        DICT.write_text("\n".join(out) + "\n", encoding="utf-8")
        print("записано:", DICT)
    else:
        print("сухой прогон (--write чтобы применить)")


if __name__ == "__main__":
    main()
