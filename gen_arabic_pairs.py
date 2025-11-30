#!/usr/bin/env python3
"""
Generate Arabic two-word password candidates with optional digit suffixes.

Generates combinations like:
  - كلمة سر
  - محمد علي
  - كلمة سر123
  - محمد علي2019

Uses linguistic filtering to reduce search space by ~75-80%.

Usage:
    # Generate 3+4 letter word pairs (no digits)
    python3 gen_arabic_pairs.py 3 4

    # Generate 4+4 letter word pairs with 0-4 digit suffix
    python3 gen_arabic_pairs.py 4 4 --digits 0-4

    # Pipe directly to hashcat
    python3 gen_arabic_pairs.py 3 4 --digits 4 | hashcat -m 22100 hash.txt -a 0

    # Generate to file first (for resumable attacks)
    python3 gen_arabic_pairs.py 4 4 --digits 2-4 > pairs_4_4.txt
    hashcat -m 22100 hash.txt -a 0 pairs_4_4.txt
"""

import sys
import argparse
from itertools import product

# Character sets based on position constraints
# First position: excludes ة ى ؤ ئ (can't start words)
FIRST_CHARS = 'ابتثجحخدذرزسشصضطظعغفقكلمنهويأإآ'

# Middle positions: excludes ء ة ى (can't be in middle)
MIDDLE_CHARS = 'ابتثجحخدذرزسشصضطظعغفقكلمنهويأإآؤئ'

# Last position: all valid
LAST_CHARS = 'ءابتثجحخدذرزسشصضطظعغفقكلمنهويأإآؤئةى'

# Vowel letters (حروف العلة)
VOWELS = frozenset('اوي')

# Bad consecutive patterns
BAD_DOUBLES = ('اا', 'وو', 'يي', 'ءء')


def is_likely_arabic_word(seq: str) -> bool:
    """Fast heuristic to filter unlikely Arabic words."""
    length = len(seq)

    # Must have vowel letter for words >= 4 chars
    if length >= 4:
        if not any(c in VOWELS for c in seq):
            return False

    # Check bad double patterns
    for bad in BAD_DOUBLES:
        if bad in seq:
            return False

    # ء not in middle
    if length > 2 and 'ء' in seq[1:-1]:
        return False

    return True


def generate_words(length: int):
    """Generate all linguistically plausible Arabic words of given length."""
    if length < 2:
        # Single char words - just use first chars
        for c in FIRST_CHARS:
            yield c
        return

    if length == 2:
        # Two char: first + last
        for first in FIRST_CHARS:
            for last in LAST_CHARS:
                word = first + last
                if is_likely_arabic_word(word):
                    yield word
        return

    # 3+ chars: first + middle(s) + last
    middle_count = length - 2

    for first in FIRST_CHARS:
        for middles in product(MIDDLE_CHARS, repeat=middle_count):
            for last in LAST_CHARS:
                word = first + ''.join(middles) + last
                if is_likely_arabic_word(word):
                    yield word


def generate_digit_suffixes(min_digits: int, max_digits: int):
    """Generate digit suffixes from min to max length."""
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


def estimate_candidates(len1: int, len2: int, min_digits: int, max_digits: int) -> int:
    """Rough estimate of candidate count."""
    # Rough estimate: 32 first × 33^(mid) × 36 last × 0.25 (filter)
    def word_estimate(length):
        if length == 1:
            return 32
        elif length == 2:
            return 32 * 36 * 0.9
        else:
            return 32 * (33 ** (length - 2)) * 36 * 0.25

    word_pairs = word_estimate(len1) * word_estimate(len2)

    digit_count = 0
    if min_digits == 0:
        digit_count = 1
    for d in range(max(1, min_digits), max_digits + 1):
        digit_count += 10 ** d

    return int(word_pairs * digit_count)


def main():
    parser = argparse.ArgumentParser(
        description='Generate Arabic two-word password candidates',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('len1', type=int, help='Length of first word (1-8)')
    parser.add_argument('len2', type=int, help='Length of second word (1-8)')
    parser.add_argument('--digits', '-d', type=str, default='0',
                        help='Digit suffix: "4" for exactly 4, "0-4" for 0 to 4, "2-4" for 2 to 4')
    parser.add_argument('--estimate', '-e', action='store_true',
                        help='Only show estimate, do not generate')
    parser.add_argument('--separator', '-s', type=str, default=' ',
                        help='Separator between words (default: space)')

    args = parser.parse_args()

    min_digits, max_digits = parse_digit_range(args.digits)

    estimate = estimate_candidates(args.len1, args.len2, min_digits, max_digits)

    if args.estimate:
        print(f"Estimated candidates: {estimate:,}", file=sys.stderr)
        return

    print(f"Generating ~{estimate:,} candidates ({args.len1}+{args.len2} words, {args.digits} digits)...",
          file=sys.stderr)

    count = 0
    for word1 in generate_words(args.len1):
        for word2 in generate_words(args.len2):
            base = word1 + args.separator + word2
            for suffix in generate_digit_suffixes(min_digits, max_digits):
                print(base + suffix)
                count += 1

    print(f"Generated {count:,} candidates", file=sys.stderr)


if __name__ == '__main__':
    main()
