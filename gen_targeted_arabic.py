#!/usr/bin/env python3
"""
Targeted Arabic password generator for family names.
Names: يحيى، نور، سنا، عثمان، ماجد
"""

import itertools
import sys

# Name variations in Arabic
NAMES = {
    'yahya': ['يحيى', 'يحيا', 'يحي'],
    'nour': ['نور', 'نورا', 'نوره', 'نورة'],
    'sana': ['سنا', 'سناء', 'سنى'],
    'othman': ['عثمان', 'عصمان'],
    'majed': ['ماجد', 'مجد', 'مجيد'],
}

# Flatten all name variations
ALL_NAMES = []
for variants in NAMES.values():
    ALL_NAMES.extend(variants)

# Special characters
SPECIALS = ['', '!', '@', '#', '$', '%', '&', '*', '_', '-', '.', '+', '=']

# Gregorian Years
YEARS = [str(y) for y in range(1900, 2026)]
SHORT_YEARS = [str(y)[2:] for y in range(1950, 2026)]  # 50-25

# Hijri Years (Islamic calendar)
# Current year ~1446 AH (2024 CE)
# Range: 1300-1446 covers roughly 1882-2024 CE
HIJRI_YEARS = [str(y) for y in range(1300, 1447)]
SHORT_HIJRI = [str(y)[2:] for y in range(1400, 1447)]  # 00-46 (1400-1446)

# Combined all years
ALL_YEARS = YEARS + SHORT_YEARS + HIJRI_YEARS + SHORT_HIJRI

# Common separators
SEPARATORS = ['', ' ', '_', '-', '.', '@', '#']

# Arabic digits (Eastern Arabic numerals) - optional
ARABIC_DIGITS = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩']

def char_len(s):
    """Count characters (not bytes) for length validation"""
    return len(s)

def generate_name_year():
    """Pattern: Name + special + year (Gregorian + Hijri)"""
    for name in ALL_NAMES:
        for spec in SPECIALS:
            for year in ALL_YEARS:
                pwd = f"{name}{spec}{year}"
                if 8 <= char_len(pwd) <= 20:
                    yield pwd

def generate_year_name():
    """Pattern: Year + special + name (Gregorian + Hijri)"""
    for year in ALL_YEARS:
        for spec in SPECIALS:
            for name in ALL_NAMES:
                pwd = f"{year}{spec}{name}"
                if 8 <= char_len(pwd) <= 20:
                    yield pwd

def generate_name_space_year():
    """Pattern: Name + space + year (common Arabic pattern, Gregorian + Hijri)"""
    for name in ALL_NAMES:
        for year in ALL_YEARS:
            pwd = f"{name} {year}"
            if 8 <= char_len(pwd) <= 20:
                yield pwd
            # Also with special after space
            for spec in SPECIALS[1:]:
                pwd = f"{name} {spec}{year}"
                if 8 <= char_len(pwd) <= 20:
                    yield pwd

def generate_name_special_name():
    """Pattern: Name + separator + name"""
    for name1 in ALL_NAMES:
        for sep in SEPARATORS:
            for name2 in ALL_NAMES:
                pwd = f"{name1}{sep}{name2}"
                if 8 <= char_len(pwd) <= 20:
                    yield pwd

def generate_name_name_year():
    """Pattern: Name + separator + name + year (Gregorian + Hijri)"""
    for name1 in ALL_NAMES:
        for sep in SEPARATORS:
            for name2 in ALL_NAMES:
                for year in SHORT_YEARS + SHORT_HIJRI + ['2020', '2021', '2022', '2023', '2024', '1440', '1441', '1442', '1443', '1444', '1445', '1446']:
                    pwd = f"{name1}{sep}{name2}{year}"
                    if 8 <= char_len(pwd) <= 20:
                        yield pwd

def generate_name_digits():
    """Pattern: Name + 1-4 digits"""
    for name in ALL_NAMES:
        # 1 digit
        for d in range(10):
            pwd = f"{name}{d}"
            if 8 <= char_len(pwd) <= 20:
                yield pwd
        # 2 digits
        for d in range(100):
            pwd = f"{name}{d:02d}"
            if 8 <= char_len(pwd) <= 20:
                yield pwd
        # 3 digits
        for d in range(1000):
            pwd = f"{name}{d:03d}"
            if 8 <= char_len(pwd) <= 20:
                yield pwd
        # 4 digits (includes years)
        for d in range(10000):
            pwd = f"{name}{d:04d}"
            if 8 <= char_len(pwd) <= 20:
                yield pwd

def generate_name_space_digits():
    """Pattern: Name + space + digits (common Arabic pattern)"""
    for name in ALL_NAMES:
        # 1-4 digits with space
        for d in range(10):
            pwd = f"{name} {d}"
            if 8 <= char_len(pwd) <= 20:
                yield pwd
        for d in range(100):
            pwd = f"{name} {d:02d}"
            if 8 <= char_len(pwd) <= 20:
                yield pwd
        for d in range(1000):
            pwd = f"{name} {d:03d}"
            if 8 <= char_len(pwd) <= 20:
                yield pwd
        for d in range(10000):
            pwd = f"{name} {d:04d}"
            if 8 <= char_len(pwd) <= 20:
                yield pwd

def generate_name_special_digits():
    """Pattern: Name + special + digits"""
    for name in ALL_NAMES:
        for spec in SPECIALS[1:]:  # Skip empty
            for d in range(10000):
                pwd = f"{name}{spec}{d}"
                if 8 <= char_len(pwd) <= 20:
                    yield pwd

def generate_common_arabic_patterns():
    """Common Arabic password patterns"""
    # Common prefixes/suffixes in Arabic
    prefixes = ['يا', 'ال', 'أنا', 'حب', 'نور']
    suffixes = ['ي', 'تي', 'نا', 'كم']

    for name in ALL_NAMES:
        # With prefixes
        for prefix in prefixes:
            pwd = f"{prefix}{name}"
            if 8 <= char_len(pwd) <= 20:
                yield pwd
            # prefix + name + year
            for year in SHORT_YEARS:
                pwd = f"{prefix}{name}{year}"
                if 8 <= char_len(pwd) <= 20:
                    yield pwd

        # With suffixes
        for suffix in suffixes:
            pwd = f"{name}{suffix}"
            if 8 <= char_len(pwd) <= 20:
                yield pwd
            # name + suffix + year
            for year in SHORT_YEARS:
                pwd = f"{name}{suffix}{year}"
                if 8 <= char_len(pwd) <= 20:
                    yield pwd

def generate_religious_patterns():
    """Religious/common Arabic phrases with names"""
    religious = ['الله', 'محمد', 'رب', 'حمد']

    for name in ALL_NAMES:
        for rel in religious:
            # name + religious
            pwd = f"{name}{rel}"
            if 8 <= char_len(pwd) <= 20:
                yield pwd
            pwd = f"{name} {rel}"
            if 8 <= char_len(pwd) <= 20:
                yield pwd
            # religious + name
            pwd = f"{rel}{name}"
            if 8 <= char_len(pwd) <= 20:
                yield pwd
            pwd = f"{rel} {name}"
            if 8 <= char_len(pwd) <= 20:
                yield pwd
            # with year
            for year in SHORT_YEARS:
                pwd = f"{name}{rel}{year}"
                if 8 <= char_len(pwd) <= 20:
                    yield pwd

def generate_love_patterns():
    """Love/family related patterns"""
    love_words = ['حب', 'حبي', 'حبيب', 'حبيبي', 'حبيبتي', 'عمر', 'عمري', 'روح', 'روحي', 'قلب', 'قلبي']

    for name in ALL_NAMES:
        for love in love_words:
            pwd = f"{love}{name}"
            if 8 <= char_len(pwd) <= 20:
                yield pwd
            pwd = f"{love} {name}"
            if 8 <= char_len(pwd) <= 20:
                yield pwd
            pwd = f"{name}{love}"
            if 8 <= char_len(pwd) <= 20:
                yield pwd
            pwd = f"{name} {love}"
            if 8 <= char_len(pwd) <= 20:
                yield pwd
            # with year (Gregorian + Hijri)
            for year in ['2020', '2021', '2022', '2023', '2024', '1440', '1441', '1442', '1443', '1444', '1445', '1446']:
                pwd = f"{love}{name}{year}"
                if 8 <= char_len(pwd) <= 20:
                    yield pwd

def main():
    seen = set()
    count = 0

    generators = [
        ("name_year", generate_name_year),
        ("year_name", generate_year_name),
        ("name_space_year", generate_name_space_year),
        ("name_special_name", generate_name_special_name),
        ("name_name_year", generate_name_name_year),
        ("name_digits", generate_name_digits),
        ("name_space_digits", generate_name_space_digits),
        ("name_special_digits", generate_name_special_digits),
        ("common_arabic_patterns", generate_common_arabic_patterns),
        ("religious_patterns", generate_religious_patterns),
        ("love_patterns", generate_love_patterns),
    ]

    for gen_name, gen_func in generators:
        for pwd in gen_func():
            if pwd not in seen:
                seen.add(pwd)
                print(pwd)
                count += 1

    print(f"# Total: {count} passwords generated", file=sys.stderr)

if __name__ == "__main__":
    main()
