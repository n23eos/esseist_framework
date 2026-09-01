#!/usr/bin/env python3
"""L1-гардрейлы: детерминированный гейт для черновика.

Использование:
    python3 l1_guardrails.py <draft.md> [--format essay|tg-post|x-thread|youtube-script]

Выход 0 = PASS, 1 = FAIL (список нарушений в stdout). Это гейт, не оценка:
проверяются только жёсткие запреты и лимиты формата. Качество меряют слои L2/L3
(см. README.md рядом).
"""
import argparse
import re
import sys
import unicodedata
from pathlib import Path

# Жёсткие запреты (FAIL) — то, что живой автор не пишет никогда
# (essayist/references/ru-slop.md: А8, А3, Б7, А13)
BANNED_PHRASES = [
    "важно отметить", "стоит отметить",  # А8 переход-анонс
    "подводя итог", "в заключение",      # А3 бантик-финал
    "в современном мире", "на сегодняшний день",  # Б7 стоп-слова
    "надеюсь, это поможет", "дайте знать",        # А13 артефакты диалога
]

# Стилистические конструкции (WARN, гейт не роняют) — могут быть авторскими,
# провенанс решает человек по ru-slop.md «Защита голоса» (А1)
SOFT_PATTERNS = [
    (r"не только[^.!?\n]{0,60}, но и", "негативный параллелизм «не только…, но и»"),
    (r"не просто[^.!?\n]{0,60}[,—]\s*а?\s", "негативный параллелизм «не просто…, а/—»"),
]

# Копипаст-артефакты (класс A: один найден — мгновенный FAIL)
ARTIFACT_PATTERNS = [
    r"oaicite", r"turn\d+(search|fetch|file)\d+", r"utm_source=(chatgpt|openai)",
    r"\[cite:\s*\d+\]", r"sandbox:/mnt/", r"</?think>", r"contentReference",
]

# Матзнаки в прозе (Б10); минус и дефис не трогаем
MATH_SIGNS = re.compile(r"[=→←⇒≥≤≠≈±]|\s(?:>|<|\+|vs)\s")

# Лимиты форматов: (единица, потолок). None = лимит берётся из меты сессии.
FORMAT_LIMITS = {
    "tg-post": ("chars", 900),
    "x-thread": ("tweet_chars", 280),
    "essay": (None, None),
    "youtube-script": (None, None),
}

MAX_EXCLAMATIONS_PER_1000_WORDS = 2
MAX_BULLET_LINES = 0  # эссе и посты — проза; списки запрещены (ru-slop В5)


def is_emoji(char: str) -> bool:
    return unicodedata.category(char) == "So" or 0x1F000 <= ord(char) <= 0x1FAFF


def check(text: str, fmt: str) -> tuple[list[str], list[str]]:
    violations = []
    warnings = []
    lower = text.lower()
    words = re.findall(r"\w+", text)
    word_count = max(len(words), 1)

    for phrase in BANNED_PHRASES:
        count = lower.count(phrase)
        if count:
            violations.append(f"запрещённая фраза «{phrase}» ×{count}")

    for pattern, label in SOFT_PATTERNS:
        count = len(re.findall(pattern, lower))
        if count:
            warnings.append(f"{label} ×{count} — авторское? сверить с session.md")

    for pattern in ARTIFACT_PATTERNS:
        if re.search(pattern, text):
            violations.append(f"копипаст-артефакт /{pattern}/")

    for match in MATH_SIGNS.finditer(text):
        violations.append(f"матзнак в прозе: «{match.group().strip()}»")
        break  # одного сообщения достаточно

    emoji_count = sum(1 for char in text if is_emoji(char))
    if emoji_count:
        violations.append(f"эмодзи ×{emoji_count}")

    exclamations = text.count("!")
    limit = MAX_EXCLAMATIONS_PER_1000_WORDS * word_count / 1000
    if exclamations > max(limit, 1):
        violations.append(f"восклицания: {exclamations} на {word_count} слов")

    bullet_lines = [ln for ln in text.splitlines() if re.match(r"\s*[-*•]\s", ln)]
    if len(bullet_lines) > MAX_BULLET_LINES:
        violations.append(f"буллет-строки ×{len(bullet_lines)} (проза, не список)")

    unit, cap = FORMAT_LIMITS.get(fmt, (None, None))
    if unit == "chars" and len(text) > cap:
        violations.append(f"объём {len(text)} знаков > лимита {cap} ({fmt})")
    if unit == "tweet_chars":
        blocks = [b.strip() for b in re.split(r"\n{2,}", text) if b.strip()]
        for i, block in enumerate(blocks, 1):
            if len(block) > cap:
                violations.append(f"твит {i}: {len(block)} знаков > {cap}")

    return violations, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="L1-гардрейлы черновика")
    parser.add_argument("draft", type=Path)
    parser.add_argument("--format", default="essay", choices=list(FORMAT_LIMITS))
    args = parser.parse_args()

    if not args.draft.is_file():
        print(f"FAIL: файл не найден: {args.draft}")
        return 1

    text = args.draft.read_text(encoding="utf-8")
    violations, warnings = check(text, args.format)

    for w in warnings:
        print(f"  WARN {w}")
    if violations:
        print(f"FAIL ({len(violations)}):")
        for v in violations:
            print(f"  - {v}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
