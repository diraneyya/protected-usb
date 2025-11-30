#!/usr/bin/env python3
"""
Unified Arabic password generator combining root-based words with common patterns.

Generates candidates like:
  - محمد
  - محمد علي
  - محمد علي2019
  - محمد علي@2019
  - ابو محمد
  - ابومحمد
  - أبو علي@2019
  - المحمد
  - عبدالله
  - عبد الله2019

Features:
  - Root-based word generation using Arabic patterns (أوزان)
  - Common prefixes: ال، أبو، ابو، عبد، ام، أم، بن، ابن
  - Two-word combinations with/without space
  - Optional @ separator before year
  - Year suffix (1990-2025 + common numbers)

================================================================================
HASHCAT USAGE EXAMPLES
================================================================================

# Quick test - single words only (~5K candidates)
python3 gen_arabic_passwords.py --mode single | hashcat -m 22100 hash.txt -a 0

# Single words + years (~400K candidates)
python3 gen_arabic_passwords.py --mode single --year --at | hashcat -m 22100 hash.txt -a 0

# Word pairs with space (~10M candidates) - RECOMMENDED FIRST
python3 gen_arabic_passwords.py --mode pairs | hashcat -m 22100 hash.txt -a 0

# Word pairs + years (~800M candidates)
python3 gen_arabic_passwords.py --mode pairs --year --at | hashcat -m 22100 hash.txt -a 0

# Full attack - all combinations (~1.6B candidates)
python3 gen_arabic_passwords.py --mode full | hashcat -m 22100 hash.txt -a 0

================================================================================
RECOMMENDED ATTACK ORDER (fastest to slowest)
================================================================================

1. Single words (fast):
   python3 gen_arabic_passwords.py -m single | hashcat -m 22100 hash.txt -a 0

2. Single words + year:
   python3 gen_arabic_passwords.py -m single -y -a | hashcat -m 22100 hash.txt -a 0

3. Word pairs (medium):
   python3 gen_arabic_passwords.py -m pairs | hashcat -m 22100 hash.txt -a 0

4. Word pairs + year (slow):
   python3 gen_arabic_passwords.py -m pairs -y | hashcat -m 22100 hash.txt -a 0

5. Full attack (very slow):
   python3 gen_arabic_passwords.py -m full | hashcat -m 22100 hash.txt -a 0

================================================================================
SAVING TO FILE (for resumable attacks)
================================================================================

# Generate once, attack multiple times
python3 gen_arabic_passwords.py -m pairs -y > arabic_pairs.txt
hashcat -m 22100 hash.txt -a 0 arabic_pairs.txt --status --status-timer=60

# Resume interrupted attack
hashcat -m 22100 hash.txt -a 0 arabic_pairs.txt --restore

================================================================================
CANDIDATE ESTIMATES
================================================================================

Mode          | No year | With year | With year+@
--------------|---------|-----------|-------------
single        | 5K      | 200K      | 400K
pairs (space) | 10M     | 400M      | 800M
pairs (no sp) | 10M     | 400M      | 800M
full          | 20M     | 800M      | 1.6B

================================================================================
"""

import sys
import argparse
from itertools import product
from pathlib import Path

# === COMMON ARABIC ROOTS ===
# Top ~100 roots that generate common names and words
COMMON_ROOTS = [
    # Names (very common in passwords)
    'حمد', 'علم', 'سلم', 'عبد', 'حسن', 'كرم', 'جمل', 'نور', 'صلح', 'فتح',
    'خلد', 'رحم', 'عزز', 'صدق', 'نصر', 'فرح', 'سعد', 'مجد', 'هدي', 'فضل',
    'جلل', 'عدل', 'قدر', 'امن', 'وجد', 'كتب', 'قول', 'عمل', 'درس', 'فهم',
    # Common verbs/nouns
    'سمع', 'نظر', 'جلس', 'اكل', 'شرب', 'نوم', 'قوم', 'مشي', 'ركب', 'سكن',
    'خرج', 'دخل', 'حمل', 'نقل', 'طلب', 'بحث', 'عرف', 'جمع', 'صنع', 'بني',
    'ملك', 'سفر', 'خدم', 'لبس', 'غسل', 'طبخ', 'كسر', 'فتح', 'غلق', 'ربح',
    # Religious/cultural
    'صلو', 'زكو', 'صوم', 'حجج', 'توب', 'غفر', 'شكر', 'صبر', 'حلم', 'خلق',
    # Family
    'ولد', 'زوج', 'اخو', 'ابو', 'امم', 'بنت', 'عمم', 'خال',
]

# === WORD PATTERNS (أوزان) ===
PATTERNS = [
    'فعل',      # كتب
    'فاعل',     # كاتب، حامد
    'فعيل',     # كريم، حميد، جميل
    'فعول',     # صبور
    'فعال',     # كتاب، جمال
    'مفعل',     # مكتب، محمد (kind of)
    'مفعول',    # مكتوب، محمود
    'افعل',     # أكبر، أحمد
    'فعلي',     # عربي، علي
    'فعلان',    # سلمان، عثمان
    'فعالة',    # كتابة، سلامة
    'تفعيل',    # تكبير
]

# === PREFIXES ===
# Common prefixes that attach to names/words
PREFIXES = [
    ('', ''),           # No prefix
    ('ال', ''),         # The (attached): المحمد
    ('ال', ' '),        # The (space): ال محمد (less common)
    ('ابو', ' '),       # Father of (space): ابو محمد
    ('ابو', ''),        # Father of (attached): ابومحمد
    ('أبو', ' '),       # Father of with hamza: أبو محمد
    ('أبو', ''),        # أبومحمد
    ('عبد', ' '),       # Servant of (space): عبد الله
    ('عبد', ''),        # Servant of (attached): عبدالله
    ('ام', ' '),        # Mother of: ام محمد
    ('ام', ''),         # اممحمد
    ('أم', ' '),        # أم محمد
    ('أم', ''),         # أممحمد
    ('بن', ' '),        # Son of: بن علي
    ('بن', ''),         # بنعلي
    ('ابن', ' '),       # Son of: ابن علي
    ('ابن', ''),        # ابنعلي
]

# Simplified prefixes for faster generation
SIMPLE_PREFIXES = [
    ('', ''),
    ('ال', ''),
    ('ابو', ' '),
    ('ابو', ''),
    ('عبد', ''),
    ('عبد', ' '),
]

# === YEARS ===
# Common years for password suffixes
YEARS = [str(y) for y in range(1990, 2026)] + ['123', '1234', '12345']

# === BAD PATTERNS ===
BAD_DOUBLES = frozenset(['اا', 'وو', 'يي', 'ءء'])


def has_bad_doubles(word: str) -> bool:
    """Check if word contains invalid doubled letters."""
    for bad in BAD_DOUBLES:
        if bad in word:
            return True
    for i in range(len(word) - 1):
        if word[i] == word[i + 1] and word[i] in 'اويء':
            return True
    return False


def apply_pattern(root: str, pattern: str) -> str:
    """Apply a pattern to a 3-letter root."""
    if len(root) != 3:
        return None

    f, ain, lam = root[0], root[1], root[2]

    result = []
    for c in pattern:
        if c == 'ف':
            result.append(f)
        elif c == 'ع':
            result.append(ain)
        elif c == 'ل':
            result.append(lam)
        else:
            result.append(c)

    return ''.join(result)


def generate_root_words(roots=None, patterns=None):
    """Generate words from roots using patterns."""
    if roots is None:
        roots = COMMON_ROOTS
    if patterns is None:
        patterns = PATTERNS

    seen = set()
    for root in roots:
        for pattern in patterns:
            word = apply_pattern(root, pattern)
            if word and word not in seen and not has_bad_doubles(word):
                seen.add(word)
                yield word


def generate_prefixed_words(words, prefixes=None):
    """Add prefixes to words."""
    if prefixes is None:
        prefixes = SIMPLE_PREFIXES

    for word in words:
        for prefix, sep in prefixes:
            yield prefix + sep + word


def generate_year_suffixes(with_at=False):
    """Generate year suffixes with optional @ sign."""
    yield ''  # No suffix
    for year in YEARS:
        yield year
        if with_at:
            yield '@' + year


def generate_single_words(with_prefix=True, with_year=False, with_at=False):
    """Generate single Arabic words."""
    words = list(generate_root_words())

    if with_prefix:
        words = list(generate_prefixed_words(words))

    for word in words:
        for suffix in generate_year_suffixes(with_at if with_year else False):
            if not with_year and suffix:
                continue
            yield word + suffix


def generate_word_pairs(with_prefix=True, with_year=False, with_at=False, space=True):
    """Generate two-word combinations."""
    words = list(generate_root_words())

    # First word can have prefix
    if with_prefix:
        first_words = list(generate_prefixed_words(words))
    else:
        first_words = words

    # Second word typically doesn't have prefix (except ال for construct state)
    second_words = words + ['ال' + w for w in words]

    separator = ' ' if space else ''

    for w1 in first_words:
        for w2 in second_words:
            base = w1 + separator + w2
            for suffix in generate_year_suffixes(with_at if with_year else False):
                if not with_year and suffix:
                    continue
                yield base + suffix


def generate_full(with_at=True):
    """Generate all combinations (single + pairs, with/without space, with year)."""
    seen = set()

    # Single words
    for word in generate_single_words(with_prefix=True, with_year=True, with_at=with_at):
        if word not in seen:
            seen.add(word)
            yield word

    # Word pairs with space
    for word in generate_word_pairs(with_prefix=True, with_year=True, with_at=with_at, space=True):
        if word not in seen:
            seen.add(word)
            yield word

    # Word pairs without space
    for word in generate_word_pairs(with_prefix=True, with_year=True, with_at=with_at, space=False):
        if word not in seen:
            seen.add(word)
            yield word


def estimate(mode, with_year, with_at):
    """Estimate candidate count."""
    num_roots = len(COMMON_ROOTS)
    num_patterns = len(PATTERNS)
    num_prefixes = len(SIMPLE_PREFIXES)
    num_years = len(YEARS)

    base_words = num_roots * num_patterns  # ~1200
    prefixed_words = base_words * num_prefixes  # ~7200

    year_mult = 1
    if with_year:
        year_mult = 1 + num_years  # no year + years
        if with_at:
            year_mult = 1 + num_years * 2  # no year + years + @years

    if mode == 'single':
        return prefixed_words * year_mult
    elif mode == 'pairs':
        # pairs with space
        return prefixed_words * (base_words * 2) * year_mult
    elif mode == 'full':
        single = prefixed_words * year_mult
        pairs_space = prefixed_words * (base_words * 2) * year_mult
        pairs_nospace = prefixed_words * (base_words * 2) * year_mult
        return single + pairs_space + pairs_nospace

    return 0


def main():
    parser = argparse.ArgumentParser(
        description='Unified Arabic password generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('--mode', '-m', type=str, default='single',
                        choices=['single', 'pairs', 'full'],
                        help='Generation mode: single words, word pairs, or full')
    parser.add_argument('--year', '-y', action='store_true',
                        help='Add year suffixes (1990-2025)')
    parser.add_argument('--at', '-a', action='store_true',
                        help='Include @ before year (e.g., محمد@2019)')
    parser.add_argument('--no-space', action='store_true',
                        help='For pairs mode: no space between words')
    parser.add_argument('--no-prefix', action='store_true',
                        help='Skip prefixes (ال، ابو، عبد، etc.)')
    parser.add_argument('--estimate', '-e', action='store_true',
                        help='Only show estimate, do not generate')

    args = parser.parse_args()

    if args.estimate:
        est = estimate(args.mode, args.year, args.at)
        print(f"Mode: {args.mode}", file=sys.stderr)
        print(f"Year suffix: {args.year}", file=sys.stderr)
        print(f"@ separator: {args.at}", file=sys.stderr)
        print(f"Estimated candidates: {est:,}", file=sys.stderr)
        return

    count = 0

    if args.mode == 'single':
        for word in generate_single_words(
            with_prefix=not args.no_prefix,
            with_year=args.year,
            with_at=args.at
        ):
            print(word)
            count += 1

    elif args.mode == 'pairs':
        for word in generate_word_pairs(
            with_prefix=not args.no_prefix,
            with_year=args.year,
            with_at=args.at,
            space=not args.no_space
        ):
            print(word)
            count += 1

    elif args.mode == 'full':
        for word in generate_full(with_at=args.at):
            print(word)
            count += 1

    print(f"Generated {count:,} candidates", file=sys.stderr)


if __name__ == '__main__':
    main()
