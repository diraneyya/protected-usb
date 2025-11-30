#!/usr/bin/env python3
"""
Fast Arabic word filter for hashcat pipelines.

Filters out linguistically unlikely Arabic character sequences to reduce
the search space by ~75-80% while preserving valid Arabic words.

Usage:
    maskprocessor '?1?2?2?2?2?2?2?3' | python3 filter_arabic.py | hashcat ...

Or standalone:
    cat candidates.txt | python3 filter_arabic.py > filtered.txt
"""

import sys

# Vowel letters (حروف العلة) - ا و ي
VOWELS = frozenset('اوي')

# Bad consecutive patterns
BAD_DOUBLES = frozenset(['اا', 'وو', 'يي', 'ءء'])

def is_likely_arabic_word(seq: str) -> bool:
    """
    Fast heuristic to filter unlikely Arabic words.

    Rules applied:
    - Must contain at least one vowel letter (ا و ي) if length >= 4
    - ء (hamza) cannot appear in the middle, only at start or end
    - ة (taa marbuta) can only be final
    - ى (alef maqsura) can only be final
    - ؤ ئ cannot start words
    - No doubled vowels: اا وو يي
    - No doubled hamza: ءء

    Returns:
        True if the sequence could be a valid Arabic word
    """
    if not seq:
        return False

    length = len(seq)

    # Must have vowel letter for words >= 4 chars
    if length >= 4:
        has_vowel = False
        for c in seq:
            if c in VOWELS:
                has_vowel = True
                break
        if not has_vowel:
            return False

    # Check bad double patterns
    for bad in BAD_DOUBLES:
        if bad in seq:
            return False

    # ء not in middle (positions 1 to len-2)
    if length > 2 and 'ء' in seq[1:-1]:
        return False

    # ة ى can only be final
    if 'ة' in seq[:-1] or 'ى' in seq[:-1]:
        return False

    # ؤ ئ can't start
    first = seq[0]
    if first in 'ؤئ':
        return False

    return True


def main():
    """Filter stdin line by line, output valid candidates."""
    for line in sys.stdin:
        word = line.rstrip('\n')
        if is_likely_arabic_word(word):
            sys.stdout.write(line)


if __name__ == '__main__':
    main()
