"""Pre-release check: проверка и подготовка к сборке пакета.

Запуск:
    py scripts/pre_release.py                 # стандартная проверка + очистка + тесты
    py scripts/pre_release.py --no-example    # пропустить проверку примера
    py scripts/pre_release.py --no-clean      # не чистить dist/ и кэш
    py scripts/pre_release.py --no-reinstall  # не переустанавливать пакет
    py scripts/pre_release.py --strict        # предупреждения становятся ошибками
"""
import argparse
import re
import shutil
import subprocess
import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "src" / "crispy_ipa" / "data"
RULES_SOURCE = PROJECT_ROOT / "src" / "crispy_ipa" / "eng_to_ipa_rules.py"
INIT_FILE = PROJECT_ROOT / "src" / "crispy_ipa" / "__init__.py"
PYPROJECT = PROJECT_ROOT / "pyproject.toml"
CHANGELOG = PROJECT_ROOT / "docs" / "CHANGELOG.md"
DIST_DIR = PROJECT_ROOT / "dist"

# Текстовые данные, которые парсятся при импорте crispy_ipa.transcriber.
DATA_FILES = ["en_dict.txt"]

README_FILES = ["README.md"]


# ─────────────────────────── Утилиты ───────────────────────────

def _ok(msg: str) -> None:
    print(f"✅ {msg}")


def _warn(msg: str) -> None:
    print(f"⚠  {msg}")


def _err(msg: str) -> None:
    print(f"❌ {msg}")


def _run(cmd: list[str], cwd: Path = PROJECT_ROOT) -> int:
    return subprocess.run(cmd, cwd=cwd).returncode


# ─────────────────────────── Проверки ───────────────────────────

def get_version_from_pyproject() -> str:
    content = PYPROJECT.read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
    if not match:
        raise ValueError("version not found in pyproject.toml")
    return match.group(1)


def get_version_from_init() -> str:
    """Читает __version__ через реальный импорт (учитывает importlib.metadata).

    Побочный эффект: импорт crispy_ipa.transcriber запускает parse_rules
    и parse_dict (~100 мс). Это ожидаемо — данные парсятся при импорте.
    """
    src = PROJECT_ROOT / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))

    if "crispy_ipa" in sys.modules:
        del sys.modules["crispy_ipa"]
    for key in list(sys.modules.keys()):
        if key.startswith("crispy_ipa."):
            del sys.modules[key]

    import crispy_ipa
    return crispy_ipa.__version__


def check_versions() -> tuple[bool, str | None]:
    try:
        pyproject_v = get_version_from_pyproject()
        init_v = get_version_from_init()
    except (ValueError, FileNotFoundError) as e:
        _err(f"Не удалось прочитать версию: {e}")
        return False, None
    if pyproject_v != init_v:
        _err(f"Версии не совпадают: pyproject.toml={pyproject_v}, __init__.py={init_v}")
        return False, None
    _ok(f"Версия: {pyproject_v}")
    return True, pyproject_v


def check_data_files() -> bool:
    """Проверяет, что текстовые данные и правила на месте и непустые."""
    ok = True
    for name in DATA_FILES:
        path = DATA_DIR / name
        if not path.exists():
            _err(f"Нет файла данных: {path}")
            ok = False
        elif path.stat().st_size == 0:
            _err(f"Пустой файл данных: {path}")
            ok = False

    if not RULES_SOURCE.exists():
        _err(f"Нет файла правил: {RULES_SOURCE}")
        ok = False
    elif RULES_SOURCE.stat().st_size == 0:
        _err(f"Пустой файл правил: {RULES_SOURCE}")
        ok = False

    if ok:
        _ok(f"Данные на месте ({len(DATA_FILES)} файл(ов) + eng_to_ipa_rules.py)")
    return ok



def check_changelog(version: str) -> bool:
    """CHANGELOG.md должен содержать запись для текущей версии."""
    if not CHANGELOG.exists():
        _err(f"Нет файла: {CHANGELOG}")
        return False
    content = CHANGELOG.read_text(encoding="utf-8")
    pattern = rf"^##\s*\[{re.escape(version)}\]"
    if not re.search(pattern, content, re.MULTILINE):
        _err(f"В CHANGELOG.md нет записи для версии {version}")
        print(f"   Добавь блок: ## [{version}] - YYYY-MM-DD")
        return False
    _ok(f"CHANGELOG содержит запись для {version}")
    return True


def check_readme() -> bool:
    """README файлы существуют и не пустые."""
    ok = True
    for name in README_FILES:
        path = PROJECT_ROOT / name
        if not path.exists():
            _warn(f"Нет файла: {name}")
            ok = False
        elif path.stat().st_size < 100:
            _warn(f"{name} подозрительно короткий ({path.stat().st_size} байт)")
            ok = False
    if ok:
        _ok("README файлы на месте")
    return ok


def check_git_clean() -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=PROJECT_ROOT, capture_output=True, text=True
    )
    dirty = result.stdout.strip()
    if dirty:
        _warn("Незакоммиченные изменения:")
        for line in dirty.splitlines():
            print(f"    {line}")
        return False
    _ok("Git чист")
    return True


# ─────────────────────────── Действия ───────────────────────────

def clean_dist() -> None:
    targets = [DIST_DIR, PROJECT_ROOT / "build", *PROJECT_ROOT.rglob("*.egg-info")]
    removed = []

    for path in targets:
        if path.exists():
            shutil.rmtree(path)
            removed.append(path.relative_to(PROJECT_ROOT).as_posix())

    if removed:
        _ok(f"Удалено: {', '.join(removed)}")
    else:
        _ok("Артефакты сборки не найдены")


def clean_cache() -> None:
    count = 0
    for p in PROJECT_ROOT.rglob("__pycache__"):
        shutil.rmtree(p, ignore_errors=True)
        count += 1
    for p in PROJECT_ROOT.rglob("*.pyc"):
        try:
            p.unlink()
            count += 1
        except FileNotFoundError:
            pass
    _ok(f"Удалено кэш-файлов: {count}")


def reinstall_editable() -> bool:
    """Обновляет метаданные пакета (чтобы importlib.metadata видел новую версию)."""
    print("📦 Переустановка в editable-режиме...")
    return _run([sys.executable, "-m", "pip", "install", "-e", ".", "--quiet"]) == 0


def run_example() -> bool:
    print("🚀 Проверка examples/basic_usage.py...")

    example_path = PROJECT_ROOT / "examples" / "basic_usage.py"
    if not example_path.exists():
        _err("Не найден examples/basic_usage.py")
        return False

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    result = subprocess.run(
        [sys.executable, str(example_path)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        env=env,
        encoding="utf-8",
    )

    if result.returncode == 0:
        _ok("Пример отработал успешно")
        return True

    _err("Пример упал с ошибкой:")
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return False


# ─────────────────────────── Главная ───────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Pre-release check")
    parser.add_argument("--no-clean", action="store_true", help="Не чистить dist/ и кэш")
    parser.add_argument("--no-example", action="store_true", help="Не запускать проверку примера")
    parser.add_argument("--no-reinstall", action="store_true", help="Не переустанавливать пакет")
    parser.add_argument("--strict", action="store_true", help="Предупреждения становятся ошибками")
    args = parser.parse_args()

    print("=" * 60)
    print("PRE-RELEASE CHECK")
    print("=" * 60)

    # 1. Очистка кэша и dist
    if not args.no_clean:
        clean_dist()
        clean_cache()

    # 2. Переустановка пакета (чтобы importlib.metadata / кэш подхватили новую версию)
    if not args.no_reinstall:
        if not reinstall_editable():
            _err("Не удалось переустановить пакет")
            sys.exit(1)
        _ok("Пакет переустановлен")

    # 3. Проверка версий
    ok, version = check_versions()
    if not ok or version is None:
        sys.exit(1)

    # 4. Данные и правила на месте
    if not check_data_files():
        sys.exit(1)

    # 5. CHANGELOG содержит запись для версии
    if not check_changelog(version):
        sys.exit(1)

    # 6. README (warn или fail в strict)
    readme_ok = check_readme()
    if not readme_ok and args.strict:
        _err("README проверка упала (--strict)")
        sys.exit(1)

    # 7. Git status (warn или fail в strict)
    git_ok = check_git_clean()
    if not git_ok and args.strict:
        _err("Git содержит незакоммиченные изменения (--strict)")
        sys.exit(1)
    if not git_ok:
        print("   ⚠️  Сборка возможна, но код в git не совпадает с тем, что уйдёт на PyPI.")

    # 8. Проверка рабочего примера
    if not args.no_example:
        if not run_example():
            _err("Пример упал")
            sys.exit(1)

    print()
    print("=" * 60)
    print("✅ ГОТОВО К СБОРКЕ")
    print("=" * 60)
    print("Следующие шаги:")
    print("  py -m build")
    print("  py -m twine check dist/*")
    print("  py -m twine upload dist/*")


if __name__ == "__main__":
    main()
