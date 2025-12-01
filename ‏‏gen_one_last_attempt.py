#!/usr/bin/env python3
import sys
from itertools import product

# -------------------------------------------------
# Helper: yield lowercase, Capitalized, UPPERCASE
# -------------------------------------------------
def case_variants(w):
    w = w.lower()
    yield w
    yield w.capitalize()
    yield w.upper()

# -------------------------------------------------
# Base word set
# -------------------------------------------------
names = [
    "yahya","yahia","yehya",
    "noor","nour","nur",
    "sana","sanaa","sanah",
    "othman","osman","uthman",
    "majed","majid","majedh",
    "afnan","afneen","afnon",
    "osama","ussama","ussamah","usama"
]

keywords = [
    "and","love","my","forever","with","best","only","true"
]

special = ["", "@", "#", "!", ".", "_", "-", "*", "%"]
years = range(1900, 2026)

# Build dictionary with case variants
words = []
for w in names + keywords:
    for v in case_variants(w):
        words.append(v)

# -------------------------------------------------
# MAIN GENERATOR
# -------------------------------------------------

write = sys.stdout.write

# 1-word
for a in words:
    write(a + "\n")

# 2-word combos
for a, b in product(words, repeat=2):
    for s in special:
        write(f"{a}{s}{b}\n")

# 3-word combos
for a, b, c in product(words, repeat=3):
    for s in special:
        write(f"{a}{s}{b}{s}{c}\n")

# Year combos
for a, b in product(words, repeat=2):
    for y in years:
        for s in special:
            write(f"{a}{s}{b}{s}{y}\n")
            write(f"{y}{s}{a}{s}{b}\n")
            write(f"{a}{s}{y}{s}{b}\n")
