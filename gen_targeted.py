#!/usr/bin/env python3
"""
Targeted password generator for family names with flexible combinations.
Names: Yahya, Nour, Sana, Othman, Majed (English spellings)

Usage:
  python3 gen_targeted.py [--cities] [--no-names]

Options:
  --cities     Include Jordan/Syria city names
  --no-names   Exclude family names (use only cities)
  --only-cities  Same as --cities --no-names
"""

import argparse
import itertools
import sys

# Name variations (common English spellings)
FAMILY_NAMES = {
    'yahya': ['yahya', 'yahia', 'yehya', 'yehia', 'yhya', 'yahiya', 'Yahya', 'Yahia', 'Yehya', 'Yehia', 'YAHYA', 'YAHIA'],
    'nour': ['nour', 'noor', 'nur', 'noura', 'noora', 'nura', 'Nour', 'Noor', 'Nur', 'Noura', 'NOUR', 'NOOR'],
    'sana': ['sana', 'sanaa', 'sanna', 'Sana', 'Sanaa', 'SANA', 'SANAA'],
    'othman': ['othman', 'osman', 'uthman', 'othmann', 'Othman', 'Osman', 'Uthman', 'OTHMAN', 'OSMAN'],
    'majed': ['majed', 'majid', 'maged', 'magid', 'majd', 'Majed', 'Majid', 'Maged', 'MAJED', 'MAJID'],
}

# Jordan cities (English spellings)
JORDAN_CITIES = {
    'amman': ['amman', 'Amman', 'AMMAN', 'aman', 'Aman'],
    'irbid': ['irbid', 'Irbid', 'IRBID', 'arbid', 'Arbid'],
    'zarqa': ['zarqa', 'Zarqa', 'ZARQA', 'zarka', 'Zarka'],
    'aqaba': ['aqaba', 'Aqaba', 'AQABA', 'akaba', 'Akaba'],
    'salt': ['salt', 'Salt', 'SALT', 'alsalt', 'Alsalt'],
    'madaba': ['madaba', 'Madaba', 'MADABA'],
    'karak': ['karak', 'Karak', 'KARAK', 'kerak', 'Kerak'],
    'jerash': ['jerash', 'Jerash', 'JERASH', 'jarash', 'Jarash'],
    'ajloun': ['ajloun', 'Ajloun', 'AJLOUN', 'ajlun', 'Ajlun'],
    'mafraq': ['mafraq', 'Mafraq', 'MAFRAQ'],
    'tafilah': ['tafilah', 'Tafilah', 'TAFILAH', 'tafila', 'Tafila'],
    'maan': ['maan', 'Maan', 'MAAN', "ma'an", "Ma'an"],
    'petra': ['petra', 'Petra', 'PETRA'],
    'wadi_rum': ['wadirum', 'Wadirum', 'WadiRum', 'wadi_rum'],
}

# Syria cities (English spellings)
SYRIA_CITIES = {
    'damascus': ['damascus', 'Damascus', 'DAMASCUS', 'dimashq', 'Dimashq'],
    'aleppo': ['aleppo', 'Aleppo', 'ALEPPO', 'halab', 'Halab'],
    'homs': ['homs', 'Homs', 'HOMS', 'hims', 'Hims'],
    'hama': ['hama', 'Hama', 'HAMA', 'hamah', 'Hamah'],
    'latakia': ['latakia', 'Latakia', 'LATAKIA', 'lattakia', 'Lattakia'],
    'deir_ezzor': ['deirezzor', 'DeirEzzor', 'deir_ezzor', 'deirezor', 'DeirEzor'],
    'raqqa': ['raqqa', 'Raqqa', 'RAQQA', 'rakka', 'Rakka'],
    'idlib': ['idlib', 'Idlib', 'IDLIB'],
    'daraa': ['daraa', 'Daraa', 'DARAA', 'deraa', 'Deraa'],
    'tartus': ['tartus', 'Tartus', 'TARTUS', 'tartous', 'Tartous'],
    'qamishli': ['qamishli', 'Qamishli', 'QAMISHLI', 'kamishli', 'Kamishli'],
    'palmyra': ['palmyra', 'Palmyra', 'PALMYRA', 'tadmor', 'Tadmor'],
    'suwayda': ['suwayda', 'Suwayda', 'SUWAYDA', 'sweida', 'Sweida'],
}

# Saudi Arabia cities (English spellings)
SAUDI_CITIES = {
    'riyadh': ['riyadh', 'Riyadh', 'RIYADH', 'riyad', 'Riyad'],
    'jeddah': ['jeddah', 'Jeddah', 'JEDDAH', 'jidda', 'Jidda', 'jedda', 'Jedda'],
    'mecca': ['mecca', 'Mecca', 'MECCA', 'makkah', 'Makkah'],
    'medina': ['medina', 'Medina', 'MEDINA', 'madinah', 'Madinah'],
    'dammam': ['dammam', 'Dammam', 'DAMMAM'],
    'khobar': ['khobar', 'Khobar', 'KHOBAR', 'alkhobar', 'AlKhobar'],
    'dhahran': ['dhahran', 'Dhahran', 'DHAHRAN'],
    'tabuk': ['tabuk', 'Tabuk', 'TABUK', 'tabouk', 'Tabouk'],
    'taif': ['taif', 'Taif', 'TAIF', 'tayef', 'Tayef'],
    'abha': ['abha', 'Abha', 'ABHA'],
    'khamis': ['khamis', 'Khamis', 'KHAMIS', 'khamismushait', 'KhamisMushait'],
    'jubail': ['jubail', 'Jubail', 'JUBAIL', 'jubayl', 'Jubayl'],
    'yanbu': ['yanbu', 'Yanbu', 'YANBU', 'yenbu', 'Yenbu'],
    'hofuf': ['hofuf', 'Hofuf', 'HOFUF', 'alhasa', 'AlHasa', 'ahsa', 'Ahsa'],
    'najran': ['najran', 'Najran', 'NAJRAN'],
    'jazan': ['jazan', 'Jazan', 'JAZAN', 'jizan', 'Jizan', 'gizan', 'Gizan'],
    'qatif': ['qatif', 'Qatif', 'QATIF', 'katif', 'Katif'],
    'buraidah': ['buraidah', 'Buraidah', 'BURAIDAH', 'buraydah', 'Buraydah'],
    'hail': ['hail', 'Hail', 'HAIL', 'hayel', 'Hayel'],
    'arar': ['arar', 'Arar', 'ARAR'],
    'sakaka': ['sakaka', 'Sakaka', 'SAKAKA'],
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

# Abu prefixes (only for names, not cities)
ABU_PREFIXES_EN = ['abu', 'Abu', 'ABU', 'abo', 'Abo', 'ABO']
ABU_SEPARATORS = ['', ' ', '_']

def generate_abu_variants(names_dict):
    """Generate Abu + name variants for names only"""
    abu_names = []
    for variants in names_dict.values():
        for name in variants:
            # Skip if name already starts with abu/abo
            if name.lower().startswith('abu') or name.lower().startswith('abo'):
                continue
            for abu in ABU_PREFIXES_EN:
                for sep in ABU_SEPARATORS:
                    abu_names.append(f"{abu}{sep}{name}")
    return abu_names

# Will be populated based on command line args
ALL_NAMES = []

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
        for variants in SAUDI_CITIES.values():
            names.extend(variants)
    return names

def generate_name_year(names):
    """Pattern: Name + special + year (Gregorian + Hijri)"""
    for name in names:
        for spec in SPECIALS:
            for year in ALL_YEARS:
                pwd = f"{name}{spec}{year}"
                if 8 <= len(pwd) <= 20:
                    yield pwd

def generate_year_name(names):
    """Pattern: Year + special + name (Gregorian + Hijri)"""
    for year in ALL_YEARS:
        for spec in SPECIALS:
            for name in names:
                pwd = f"{year}{spec}{name}"
                if 8 <= len(pwd) <= 20:
                    yield pwd

def generate_name_special_name(names):
    """Pattern: Name + separator + name"""
    for name1 in names:
        for sep in SEPARATORS:
            for name2 in names:
                pwd = f"{name1}{sep}{name2}"
                if 8 <= len(pwd) <= 20:
                    yield pwd

def generate_name_name_year(names):
    """Pattern: Name + separator + name + year (Gregorian + Hijri)"""
    for name1 in names:
        for sep in SEPARATORS:
            for name2 in names:
                for year in SHORT_YEARS + SHORT_HIJRI:
                    pwd = f"{name1}{sep}{name2}{year}"
                    if 8 <= len(pwd) <= 20:
                        yield pwd

def generate_name_digits(names):
    """Pattern: Name + 1-4 digits"""
    for name in names:
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

def generate_name_special_digits(names):
    """Pattern: Name + special + digits"""
    for name in names:
        for spec in SPECIALS[1:]:  # Skip empty
            for d in range(10000):
                pwd = f"{name}{spec}{d}"
                if 8 <= len(pwd) <= 20:
                    yield pwd

def generate_leet_speak(names):
    """Leet speak variants of names (with Gregorian + Hijri years)"""
    leet_map = {'a': '@', 'e': '3', 'i': '1', 'o': '0', 's': '$', 't': '7'}

    for name in names:
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

def generate_common_patterns(names):
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

    for name in names:
        for pattern in patterns:
            pwd = pattern.format(name=name)
            if 8 <= len(pwd) <= 20:
                yield pwd
            # Also with first letter capitalized
            pwd_cap = pattern.format(name=name.capitalize())
            if 8 <= len(pwd_cap) <= 20:
                yield pwd_cap

def generate_phone_patterns(names):
    """Phone number patterns - Jordan/Syria mobile prefixes"""
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
                if 8 <= len(pwd) <= 20:
                    yield pwd
            for d in range(100000):  # 00000-99999
                pwd = f"{name}{prefix}{d:05d}"
                if 8 <= len(pwd) <= 20:
                    yield pwd

        # Name + space/underscore + phone patterns
        for sep in [' ', '_', '']:
            for prefix in all_prefixes:
                for d in range(10000):
                    pwd = f"{name}{sep}{prefix}{d:04d}"
                    if 8 <= len(pwd) <= 20:
                        yield pwd

def generate_digits_4(names):
    """Name + any 4 digits (0000-9999) - covers PO boxes, pins, short codes"""
    separators = ['', ' ', '_', '-', '.']

    for name in names:
        for sep in separators:
            for d in range(10000):  # 0000-9999
                pwd = f"{name}{sep}{d:04d}"
                if 8 <= len(pwd) <= 20:
                    yield pwd
                # Also digits first
                pwd = f"{d:04d}{sep}{name}"
                if 8 <= len(pwd) <= 20:
                    yield pwd

def generate_extended_digits(names):
    """Extended digit patterns: 5-7 digits after name"""
    for name in names:
        # 5 digits
        for d in range(100000):
            pwd = f"{name}{d:05d}"
            if 8 <= len(pwd) <= 20:
                yield pwd
        # 6 digits
        for d in range(1000000):
            pwd = f"{name}{d:06d}"
            if 8 <= len(pwd) <= 20:
                yield pwd
        # 7 digits (limited - only round numbers and sequences)
        for d in range(0, 10000000, 1000):  # Every 1000th number
            pwd = f"{name}{d:07d}"
            if 8 <= len(pwd) <= 20:
                yield pwd

def main():
    parser = argparse.ArgumentParser(description='Generate targeted passwords')
    parser.add_argument('--cities', action='store_true', help='Include Jordan/Syria city names')
    parser.add_argument('--no-names', action='store_true', help='Exclude family names')
    parser.add_argument('--only-cities', action='store_true', help='Use only city names (same as --cities --no-names)')
    parser.add_argument('--phone', action='store_true', help='Include phone number patterns (large keyspace)')
    parser.add_argument('--digits4', action='store_true', help='Include any 4-digit patterns (PO boxes, pins)')
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
        ("name_special_name", generate_name_special_name),
        ("name_name_year", generate_name_name_year),
        ("name_digits", generate_name_digits),
        ("name_special_digits", generate_name_special_digits),
        ("leet_speak", generate_leet_speak),
        ("common_patterns", generate_common_patterns),
    ]

    # Add phone patterns if requested (large keyspace)
    if args.phone:
        generators.append(("phone_patterns", generate_phone_patterns))
        print("# Including phone number patterns", file=sys.stderr)

    # Add 4-digit patterns if requested (PO boxes, pins, etc.)
    if args.digits4:
        generators.append(("digits_4", generate_digits_4))
        print("# Including 4-digit patterns (0000-9999)", file=sys.stderr)

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
