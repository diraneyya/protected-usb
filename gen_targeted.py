#!/usr/bin/env python3
"""
Targeted password generator for family names with flexible combinations.
Names: Yahya, Nour, Sana, Othman, Majed (English spellings)
"""

import itertools
import sys

# Name variations (common English spellings)
NAMES = {
    'yahya': ['yahya', 'yahia', 'yehya', 'yehia', 'yhya', 'yahiya', 'Yahya', 'Yahia', 'Yehya', 'Yehia', 'YAHYA', 'YAHIA'],
    'nour': ['nour', 'noor', 'nur', 'noura', 'noora', 'nura', 'Nour', 'Noor', 'Nur', 'Noura', 'NOUR', 'NOOR'],
    'sana': ['sana', 'sanaa', 'sanna', 'Sana', 'Sanaa', 'SANA', 'SANAA'],
    'othman': ['othman', 'osman', 'uthman', 'othmann', 'Othman', 'Osman', 'Uthman', 'OTHMAN', 'OSMAN'],
    'majed': ['majed', 'majid', 'maged', 'magid', 'majd', 'Majed', 'Majid', 'Maged', 'MAJED', 'MAJID'],
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

def generate_name_year():
    """Pattern: Name + special + year (Gregorian + Hijri)"""
    for name in ALL_NAMES:
        for spec in SPECIALS:
            for year in ALL_YEARS:
                pwd = f"{name}{spec}{year}"
                if 8 <= len(pwd) <= 20:
                    yield pwd

def generate_year_name():
    """Pattern: Year + special + name (Gregorian + Hijri)"""
    for year in ALL_YEARS:
        for spec in SPECIALS:
            for name in ALL_NAMES:
                pwd = f"{year}{spec}{name}"
                if 8 <= len(pwd) <= 20:
                    yield pwd

def generate_name_special_name():
    """Pattern: Name + separator + name"""
    for name1 in ALL_NAMES:
        for sep in SEPARATORS:
            for name2 in ALL_NAMES:
                pwd = f"{name1}{sep}{name2}"
                if 8 <= len(pwd) <= 20:
                    yield pwd

def generate_name_name_year():
    """Pattern: Name + separator + name + year (Gregorian + Hijri)"""
    for name1 in ALL_NAMES:
        for sep in SEPARATORS:
            for name2 in ALL_NAMES:
                for year in SHORT_YEARS + SHORT_HIJRI:
                    pwd = f"{name1}{sep}{name2}{year}"
                    if 8 <= len(pwd) <= 20:
                        yield pwd

def generate_name_digits():
    """Pattern: Name + 1-4 digits"""
    for name in ALL_NAMES:
        # 1 digit
        for d in range(10):
            pwd = f"{name}{d}"
            if 8 <= len(pwd) <= 20:
                yield pwd
        # 2 digits
        for d in range(100):
            pwd = f"{name}{d:02d}"
            if 8 <= len(pwd) <= 20:
                yield pwd
        # 3 digits
        for d in range(1000):
            pwd = f"{name}{d:03d}"
            if 8 <= len(pwd) <= 20:
                yield pwd

def generate_name_special_digits():
    """Pattern: Name + special + digits"""
    for name in ALL_NAMES:
        for spec in SPECIALS[1:]:  # Skip empty
            for d in range(10000):
                pwd = f"{name}{spec}{d}"
                if 8 <= len(pwd) <= 20:
                    yield pwd

def generate_leet_speak():
    """Leet speak variants of names (with Gregorian + Hijri years)"""
    leet_map = {'a': '@', 'e': '3', 'i': '1', 'o': '0', 's': '$', 't': '7'}

    for name in ALL_NAMES:
        name_lower = name.lower()
        # Generate all leet combinations
        positions = [(i, c) for i, c in enumerate(name_lower) if c in leet_map]

        for r in range(1, len(positions) + 1):
            for combo in itertools.combinations(range(len(positions)), r):
                leet_name = list(name_lower)
                for idx in combo:
                    pos, char = positions[idx]
                    leet_name[pos] = leet_map[char]
                leet_str = ''.join(leet_name)

                # Add with years (Gregorian + Hijri)
                for year in ALL_YEARS:
                    pwd = f"{leet_str}{year}"
                    if 8 <= len(pwd) <= 20:
                        yield pwd
                    for spec in SPECIALS[1:]:
                        pwd = f"{leet_str}{spec}{year}"
                        if 8 <= len(pwd) <= 20:
                            yield pwd

def generate_common_patterns():
    """Common password patterns with names (Gregorian + Hijri years)"""
    patterns = [
        "{name}123", "{name}1234", "{name}12345",
        "{name}!", "{name}!!", "{name}@", "{name}@@",
        "{name}#1", "{name}@1", "{name}!1",
        "123{name}", "1234{name}",
        "{name}abc", "{name}xyz",
        "i{name}", "my{name}", "the{name}",
        "{name}love", "love{name}",
        # Gregorian years
        "{name}2020", "{name}2021", "{name}2022", "{name}2023", "{name}2024",
        # Hijri years
        "{name}1440", "{name}1441", "{name}1442", "{name}1443", "{name}1444", "{name}1445", "{name}1446",
    ]

    for name in ALL_NAMES:
        for pattern in patterns:
            pwd = pattern.format(name=name)
            if 8 <= len(pwd) <= 20:
                yield pwd
            # Also with first letter capitalized
            pwd_cap = pattern.format(name=name.capitalize())
            if 8 <= len(pwd_cap) <= 20:
                yield pwd_cap

def main():
    seen = set()
    count = 0

    generators = [
        ("name_year", generate_name_year),
        ("year_name", generate_year_name),
        ("name_special_name", generate_name_special_name),
        ("name_name_year", generate_name_name_year),
        ("name_digits", generate_name_digits),
        ("name_special_digits", generate_name_special_digits),
        ("leet_speak", generate_leet_speak),
        ("common_patterns", generate_common_patterns),
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
