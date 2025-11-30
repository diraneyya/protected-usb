#!/usr/bin/env python3
"""
Targeted Arabic password generator for family names.
Names: يحيى، نور، سنا، عثمان، ماجد

Usage:
  python3 gen_targeted_arabic.py [--cities] [--no-names]

Options:
  --cities     Include Jordan/Syria city names
  --no-names   Exclude family names (use only cities)
  --only-cities  Same as --cities --no-names
"""

import argparse
import itertools
import sys

# Name variations in Arabic
FAMILY_NAMES = {
    'yahya': ['يحيى', 'يحيا', 'يحي'],
    'nour': ['نور', 'نورا', 'نوره', 'نورة'],
    'sana': ['سنا', 'سناء', 'سنى'],
    'othman': ['عثمان', 'عصمان'],
    'majed': ['ماجد', 'مجد', 'مجيد'],
}

# Jordan cities (Arabic)
JORDAN_CITIES = {
    'amman': ['عمان', 'عمّان'],
    'irbid': ['اربد', 'إربد'],
    'zarqa': ['الزرقاء', 'زرقاء'],
    'aqaba': ['العقبة', 'عقبة'],
    'salt': ['السلط', 'سلط'],
    'madaba': ['مادبا', 'مأدبا'],
    'karak': ['الكرك', 'كرك'],
    'jerash': ['جرش'],
    'ajloun': ['عجلون'],
    'mafraq': ['المفرق', 'مفرق'],
    'tafilah': ['الطفيلة', 'طفيلة'],
    'maan': ['معان', 'معن'],
    'petra': ['البتراء', 'بترا'],
}

# Syria cities (Arabic)
SYRIA_CITIES = {
    'damascus': ['دمشق', 'الشام', 'شام'],
    'aleppo': ['حلب'],
    'homs': ['حمص'],
    'hama': ['حماة', 'حماه'],
    'latakia': ['اللاذقية', 'لاذقية'],
    'deir_ezzor': ['دير الزور', 'ديرالزور'],
    'raqqa': ['الرقة', 'رقة'],
    'idlib': ['إدلب', 'ادلب'],
    'daraa': ['درعا', 'درعة'],
    'tartus': ['طرطوس'],
    'qamishli': ['القامشلي', 'قامشلي'],
    'palmyra': ['تدمر'],
    'suwayda': ['السويداء', 'سويداء'],
}

# Special characters
SPECIALS = ['', '!', '@', '#', '$', '%', '&', '*', '_', '-', '.', '+', '=']

# Gregorian Years
YEARS = [str(y) for y in range(1900, 2026)]
SHORT_YEARS = [str(y)[2:] for y in range(1950, 2026)]  # 50-25

# Hijri Years (Islamic calendar)
HIJRI_YEARS = [str(y) for y in range(1300, 1447)]
SHORT_HIJRI = [str(y)[2:] for y in range(1400, 1447)]  # 00-46 (1400-1446)

# Combined all years
ALL_YEARS = YEARS + SHORT_YEARS + HIJRI_YEARS + SHORT_HIJRI

# Common separators
SEPARATORS = ['', ' ', '_', '-', '.', '@', '#']

# Arabic digits (Eastern Arabic numerals) - optional
ARABIC_DIGITS = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩']

# Abu prefixes (only for names, not cities)
ABU_PREFIXES_AR = ['ابو', 'أبو', 'ابو ', 'أبو ']

def generate_abu_variants(names_dict):
    """Generate Abu + name variants for Arabic names only"""
    abu_names = []
    for variants in names_dict.values():
        for name in variants:
            for abu in ABU_PREFIXES_AR:
                abu_names.append(f"{abu}{name}")
    return abu_names

def char_len(s):
    """Count characters (not bytes) for length validation"""
    return len(s)

def get_all_names(include_names=True, include_cities=False, include_abu=True):
    """Build the list of names based on options"""
    names = []
    if include_names:
        for variants in FAMILY_NAMES.values():
            names.extend(variants)
        # Add Abu + name variants (only for family names, not cities)
        if include_abu:
            names.extend(generate_abu_variants(FAMILY_NAMES))
    if include_cities:
        for variants in JORDAN_CITIES.values():
            names.extend(variants)
        for variants in SYRIA_CITIES.values():
            names.extend(variants)
    return names

def generate_name_year(names):
    """Pattern: Name + special + year (Gregorian + Hijri)"""
    for name in names:
        for spec in SPECIALS:
            for year in ALL_YEARS:
                pwd = f"{name}{spec}{year}"
                if 8 <= char_len(pwd) <= 20:
                    yield pwd

def generate_year_name(names):
    """Pattern: Year + special + name (Gregorian + Hijri)"""
    for year in ALL_YEARS:
        for spec in SPECIALS:
            for name in names:
                pwd = f"{year}{spec}{name}"
                if 8 <= char_len(pwd) <= 20:
                    yield pwd

def generate_name_space_year(names):
    """Pattern: Name + space + year (common Arabic pattern, Gregorian + Hijri)"""
    for name in names:
        for year in ALL_YEARS:
            pwd = f"{name} {year}"
            if 8 <= char_len(pwd) <= 20:
                yield pwd
            # Also with special after space
            for spec in SPECIALS[1:]:
                pwd = f"{name} {spec}{year}"
                if 8 <= char_len(pwd) <= 20:
                    yield pwd

def generate_name_special_name(names):
    """Pattern: Name + separator + name"""
    for name1 in names:
        for sep in SEPARATORS:
            for name2 in names:
                pwd = f"{name1}{sep}{name2}"
                if 8 <= char_len(pwd) <= 20:
                    yield pwd

def generate_name_name_year(names):
    """Pattern: Name + separator + name + year (Gregorian + Hijri)"""
    for name1 in names:
        for sep in SEPARATORS:
            for name2 in names:
                for year in SHORT_YEARS + SHORT_HIJRI + ['2020', '2021', '2022', '2023', '2024', '1440', '1441', '1442', '1443', '1444', '1445', '1446']:
                    pwd = f"{name1}{sep}{name2}{year}"
                    if 8 <= char_len(pwd) <= 20:
                        yield pwd

def generate_name_digits(names):
    """Pattern: Name + 1-4 digits"""
    for name in names:
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

def generate_name_space_digits(names):
    """Pattern: Name + space + digits (common Arabic pattern)"""
    for name in names:
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

def generate_name_special_digits(names):
    """Pattern: Name + special + digits"""
    for name in names:
        for spec in SPECIALS[1:]:  # Skip empty
            for d in range(10000):
                pwd = f"{name}{spec}{d}"
                if 8 <= char_len(pwd) <= 20:
                    yield pwd

def generate_common_arabic_patterns(names):
    """Common Arabic password patterns"""
    # Common prefixes/suffixes in Arabic
    prefixes = ['يا', 'ال', 'أنا', 'حب', 'نور']
    suffixes = ['ي', 'تي', 'نا', 'كم']

    for name in names:
        # With prefixes
        for prefix in prefixes:
            pwd = f"{prefix}{name}"
            if 8 <= char_len(pwd) <= 20:
                yield pwd
            # prefix + name + year
            for year in SHORT_YEARS + SHORT_HIJRI:
                pwd = f"{prefix}{name}{year}"
                if 8 <= char_len(pwd) <= 20:
                    yield pwd

        # With suffixes
        for suffix in suffixes:
            pwd = f"{name}{suffix}"
            if 8 <= char_len(pwd) <= 20:
                yield pwd
            # name + suffix + year
            for year in SHORT_YEARS + SHORT_HIJRI:
                pwd = f"{name}{suffix}{year}"
                if 8 <= char_len(pwd) <= 20:
                    yield pwd

def generate_religious_patterns(names):
    """Religious/common Arabic phrases with names"""
    religious = ['الله', 'محمد', 'رب', 'حمد']

    for name in names:
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
            for year in SHORT_YEARS + SHORT_HIJRI:
                pwd = f"{name}{rel}{year}"
                if 8 <= char_len(pwd) <= 20:
                    yield pwd

def generate_love_patterns(names):
    """Love/family related patterns"""
    love_words = ['حب', 'حبي', 'حبيب', 'حبيبي', 'حبيبتي', 'عمر', 'عمري', 'روح', 'روحي', 'قلب', 'قلبي']

    for name in names:
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

def generate_phone_patterns(names):
    """Phone number patterns - Jordan/Syria mobile prefixes + 7 digits is too large,
    so we use common patterns and shorter sequences"""
    # Common Jordan mobile prefixes (07X)
    jordan_prefixes = ['077', '078', '079']
    # Syria prefixes (09X)
    syria_prefixes = ['091', '092', '093', '094', '095', '099']

    all_prefixes = jordan_prefixes + syria_prefixes

    for name in names:
        # Name + phone prefix + 4-5 digits (manageable keyspace)
        for prefix in all_prefixes:
            for d in range(10000):  # 0000-9999
                pwd = f"{name}{prefix}{d:04d}"
                if 8 <= char_len(pwd) <= 20:
                    yield pwd
            for d in range(100000):  # 00000-99999
                pwd = f"{name}{prefix}{d:05d}"
                if 8 <= char_len(pwd) <= 20:
                    yield pwd

        # Name + space + phone patterns
        for prefix in all_prefixes:
            for d in range(10000):
                pwd = f"{name} {prefix}{d:04d}"
                if 8 <= char_len(pwd) <= 20:
                    yield pwd

def generate_extended_digits(names):
    """Extended digit patterns: 5-7 digits after name"""
    for name in names:
        # 5 digits
        for d in range(100000):
            pwd = f"{name}{d:05d}"
            if 8 <= char_len(pwd) <= 20:
                yield pwd
        # 6 digits
        for d in range(1000000):
            pwd = f"{name}{d:06d}"
            if 8 <= char_len(pwd) <= 20:
                yield pwd
        # 7 digits (limited - only round numbers and sequences)
        for d in range(0, 10000000, 1000):  # Every 1000th number
            pwd = f"{name}{d:07d}"
            if 8 <= char_len(pwd) <= 20:
                yield pwd

def main():
    parser = argparse.ArgumentParser(description='Generate targeted Arabic passwords')
    parser.add_argument('--cities', action='store_true', help='Include Jordan/Syria city names')
    parser.add_argument('--no-names', action='store_true', help='Exclude family names')
    parser.add_argument('--only-cities', action='store_true', help='Use only city names (same as --cities --no-names)')
    parser.add_argument('--phone', action='store_true', help='Include phone number patterns (large keyspace)')
    parser.add_argument('--extended', action='store_true', help='Include extended digit patterns 5-7 digits (very large)')
    args = parser.parse_args()

    # Handle --only-cities shortcut
    if args.only_cities:
        args.cities = True
        args.no_names = True

    include_names = not args.no_names
    include_cities = args.cities

    if not include_names and not include_cities:
        print("Error: Must include at least names or cities", file=sys.stderr)
        sys.exit(1)

    names = get_all_names(include_names=include_names, include_cities=include_cities)
    print(f"# Using {len(names)} name/city variations", file=sys.stderr)

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

    # Add phone patterns if requested (large keyspace)
    if args.phone:
        generators.append(("phone_patterns", generate_phone_patterns))
        print("# Including phone number patterns", file=sys.stderr)

    # Add extended digits if requested (very large keyspace)
    if args.extended:
        generators.append(("extended_digits", generate_extended_digits))
        print("# Including extended digit patterns (5-7 digits)", file=sys.stderr)

    for gen_name, gen_func in generators:
        for pwd in gen_func(names):
            if pwd not in seen:
                seen.add(pwd)
                print(pwd)
                count += 1

    print(f"# Total: {count} passwords generated", file=sys.stderr)

if __name__ == "__main__":
    main()
