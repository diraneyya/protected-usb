#!/usr/bin/env python3
"""
Generate Arabic words from 3-letter roots using common patterns (أوزان).

Arabic words are formed by applying patterns to triliteral roots.
For example, root ك-ت-ب (k-t-b) produces:
  - كاتب (فاعل) - writer
  - مكتوب (مفعول) - written
  - كتاب (فعال) - book
  - مكتبة (مفعلة) - library

This script applies the most common patterns to generate password candidates.

Usage:
    # Generate from default common_roots.txt
    python3 gen_from_roots.py | hashcat -m 22100 hash.txt -a 0

    # Generate with digit suffix
    python3 gen_from_roots.py --digits 4 | hashcat -m 22100 hash.txt -a 0

    # Use custom roots file
    python3 gen_from_roots.py --roots my_roots.txt

    # Estimate candidate count
    python3 gen_from_roots.py --estimate
"""

import sys
import argparse
from itertools import product
from pathlib import Path

# Common Arabic word patterns (أوزان)
# Each pattern is a tuple: (template, description)
# Template uses ف=first, ع=second, ل=third letter of root
PATTERNS = [
    # === BASIC VERB FORMS ===
    ('فعل', 'base verb'),           # kataba - كتب
    ('فعّل', 'intensive'),          # كتّب
    ('فاعل', 'active participle'),  # كاتب - writer
    ('فعيل', 'adjective form'),     # كريم - generous
    ('فعول', 'adjective form 2'),   # صبور - patient
    ('فعال', 'noun form'),          # كتاب - book
    ('فعالة', 'noun feminine'),     # كتابة - writing
    ('فاعلة', 'feminine participle'), # كاتبة

    # === DERIVED FORMS ===
    ('مفعل', 'place/instrument'),   # مكتب - office
    ('مفعلة', 'place feminine'),    # مكتبة - library
    ('مفعول', 'passive participle'), # مكتوب - written
    ('افعل', 'comparative/superlative'), # أكبر - bigger
    ('فعلان', 'adjective ending'),  # غضبان - angry
    ('فعلة', 'single instance'),    # ضربة - a hit

    # === NAME PATTERNS (very common in passwords) ===
    ('محمد', 'muhammad pattern'),   # Uses حمد root
    ('احمد', 'ahmad pattern'),      # أحمد
    ('فعلي', 'nisba adjective'),    # عربي - Arab
    ('فعلية', 'nisba feminine'),    # عربية

    # === EXTENDED PATTERNS ===
    ('تفعيل', 'verbal noun form II'), # تكبير - enlargement
    ('مفاعلة', 'verbal noun form III'), # مكاتبة - correspondence
    ('افعال', 'verbal noun form IV'), # إكرام - honoring
    ('تفعّل', 'form V verb'),       # تعلّم - to learn
    ('تفاعل', 'form VI verb'),      # تعاون - to cooperate
    ('انفعال', 'form VII noun'),    # انكسار - breaking
    ('افتعال', 'form VIII noun'),   # اجتماع - meeting
    ('استفعال', 'form X noun'),     # استقبال - reception

    # === PLURAL PATTERNS ===
    ('فعول', 'broken plural 1'),    # بيوت - houses
    ('افعال', 'broken plural 2'),   # أعمال - works
    ('فعلاء', 'plural form'),       # علماء - scholars
    ('فواعل', 'plural form 2'),     # كواتب - writers (f)
    ('مفاعيل', 'plural form 3'),    # مكاتيب - letters
]

# Simplified patterns for faster generation (most common in passwords)
SIMPLE_PATTERNS = [
    'فعل',      # كتب
    'فعّل',     # كتّب
    'فاعل',     # كاتب
    'فعيل',     # كريم
    'فعول',     # صبور
    'فعال',     # كتاب
    'فعالة',    # كتابة
    'مفعل',     # مكتب
    'مفعول',    # مكتوب
    'افعل',     # أكبر
    'فعلي',     # عربي
    'تفعيل',    # تكبير
]

# Letters that should not be doubled (all except shadda-valid consonants)
# Doubled vowels are invalid: اا وو يي
# Doubled hamza is invalid: ءء
BAD_DOUBLES = frozenset(['اا', 'وو', 'يي', 'ءء'])


def has_bad_doubles(word: str) -> bool:
    """Check if word contains invalid doubled letters."""
    for bad in BAD_DOUBLES:
        if bad in word:
            return True
    # Also check for any consecutive identical letters (except shadda cases)
    for i in range(len(word) - 1):
        if word[i] == word[i + 1]:
            # Allow doubled consonants that can take shadda (like كتّب)
            # But flag doubled vowels and hamza
            if word[i] in 'اويء':
                return True
    return False


def apply_pattern(root: str, pattern: str) -> str:
    """
    Apply a pattern to a 3-letter root.

    Pattern uses: ف=first, ع=second, ل=third letter
    """
    if len(root) != 3:
        return None

    f, ain, lam = root[0], root[1], root[2]

    result = []
    i = 0
    while i < len(pattern):
        c = pattern[i]
        if c == 'ف':
            result.append(f)
        elif c == 'ع':
            result.append(ain)
        elif c == 'ل':
            result.append(lam)
        elif c == 'ّ':  # shadda - double previous
            if result:
                result.append(result[-1])
        else:
            result.append(c)
        i += 1

    return ''.join(result)


def load_roots(filepath: str) -> list:
    """Load roots from file, skipping comments and empty lines."""
    roots = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # Handle both "كتب" and "ك-ت-ب" formats
                root = line.replace('-', '').replace(' ', '')
                if len(root) == 3:
                    roots.append(root)
    return roots


def generate_digit_suffixes(min_digits: int, max_digits: int):
    """Generate digit suffixes."""
    if min_digits == 0:
        yield ''
    for num_digits in range(max(1, min_digits), max_digits + 1):
        for digits in product('0123456789', repeat=num_digits):
            yield ''.join(digits)


def parse_digit_range(digit_spec: str) -> tuple:
    """Parse digit specification like '4', '0-4', '2-4'."""
    if '-' in digit_spec:
        parts = digit_spec.split('-')
        return int(parts[0]), int(parts[1])
    else:
        n = int(digit_spec)
        return n, n


def main():
    parser = argparse.ArgumentParser(
        description='Generate Arabic words from roots using common patterns',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('--roots', '-r', type=str,
                        default=str(Path(__file__).parent / 'common_roots.txt'),
                        help='Path to roots file (default: common_roots.txt)')
    parser.add_argument('--digits', '-d', type=str, default='0',
                        help='Digit suffix: "4" for exactly 4, "0-4" for range')
    parser.add_argument('--estimate', '-e', action='store_true',
                        help='Only show estimate, do not generate')
    parser.add_argument('--full', '-f', action='store_true',
                        help='Use full pattern set (slower, more words)')
    parser.add_argument('--patterns', '-p', action='store_true',
                        help='List available patterns and exit')

    args = parser.parse_args()

    if args.patterns:
        print("Available patterns:")
        for pattern, desc in PATTERNS:
            example = apply_pattern('كتب', pattern)
            print(f"  {pattern:12} ({desc:25}) -> {example}")
        return

    patterns = PATTERNS if args.full else [(p, '') for p in SIMPLE_PATTERNS]
    min_digits, max_digits = parse_digit_range(args.digits)

    # Load roots
    try:
        roots = load_roots(args.roots)
    except FileNotFoundError:
        print(f"Error: Roots file not found: {args.roots}", file=sys.stderr)
        sys.exit(1)

    # Calculate digit multiplier
    digit_count = 0
    if min_digits == 0:
        digit_count = 1
    for d in range(max(1, min_digits), max_digits + 1):
        digit_count += 10 ** d

    estimate = len(roots) * len(patterns) * digit_count

    if args.estimate:
        print(f"Roots: {len(roots)}", file=sys.stderr)
        print(f"Patterns: {len(patterns)}", file=sys.stderr)
        print(f"Digit combinations: {digit_count}", file=sys.stderr)
        print(f"Estimated candidates: {estimate:,}", file=sys.stderr)
        return

    print(f"Generating from {len(roots)} roots × {len(patterns)} patterns...",
          file=sys.stderr)

    count = 0
    seen = set()  # Deduplicate

    skipped = 0
    for root in roots:
        for pattern, _ in patterns:
            word = apply_pattern(root, pattern)
            if word and word not in seen:
                seen.add(word)
                # Skip words with bad doubled letters
                if has_bad_doubles(word):
                    skipped += 1
                    continue
                for suffix in generate_digit_suffixes(min_digits, max_digits):
                    print(word + suffix)
                    count += 1

    if skipped:
        print(f"Skipped {skipped} words with invalid doubled letters", file=sys.stderr)

    print(f"Generated {count:,} unique candidates", file=sys.stderr)


if __name__ == '__main__':
    main()
