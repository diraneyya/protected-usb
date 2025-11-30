# BitLocker Recovery Project

This directory contains tools and documentation for recovering a BitLocker-encrypted USB drive.

## Project Overview

- **Target**: Sony USB 3.0 (16.2 GB) BitLocker To Go encrypted drive
- **Encryption Date**: September 16, 2019
- **BitLocker Version**: 2 (Windows 7 or later)
- **Encryption Method**: AES-CCM with 1,048,576 SHA-256 iterations

## Files

| File | Purpose |
|------|---------|
| `README.md` | Full analysis report and decryption options |
| `H100-SETUP.md` | GPU cracking setup guide (H100/RTX 4090) |
| `arabic_attack.hcmask` | Hashcat mask file for Arabic password attacks |
| `hashes.txt` | All extracted BitLocker hashes |
| `user_password_hash.txt` | User password hash for cracking |

## Hash Information

The extracted hash uses mode `22100` in hashcat:
```
$bitlocker$0$16$b3b78555e45367d2d735588ffe89ce85$1048576$12$90e2969ca76cd50103000000$60$...
```

## Quick Commands

### Test a single password guess
```bash
echo "your_guess" | john --format=bitlocker ~/bitlocker-recovery/hashes.txt --stdin
```

### Check if password was found
```bash
cat ~/.local/share/hashcat/hashcat.potfile
```

### Run Arabic mask attack
```bash
hashcat -m 22100 -a 3 -w 3 hash.txt arabic_attack.hcmask
```

## Arabic Attack Strategy

The `arabic_attack.hcmask` file uses linguistic rules to reduce search space:

- **Position-aware charsets**: Different valid letters for start/middle/end positions
- **Linguistic constraints**: ة ى only at end, ء not in middle, etc.
- **~42% reduction** from position rules alone
- **~80% reduction** with full linguistic filtering (using `filter_arabic.py`)

### Character Sets
- `?1` = First position (32 letters - excludes ة ى ؤ ئ)
- `?2` = Middle positions (33 letters - excludes ء ة ى)
- `?3` = Last position (36 letters - all valid)

## Performance Benchmarks

| Hardware | BitLocker Speed |
|----------|-----------------|
| M2 Pro (Mac) | ~469 H/s |
| RTX 4090 | ~15,000 H/s |
| 4x RTX 4090 | ~60,000 H/s |
| H100 | ~50,000-80,000 H/s |

## Attack Priority

1. Dictionary attacks (rockyou.txt)
2. Dictionary + rules (best64.rule)
3. Arabic patterns (4-8 letters + digits)
4. Brute force (short passwords only)

## Server Connections

```bash
# 4x RTX 4090 server
ssh -p 40867 root@213.181.123.59

# Single RTX 4090 server
ssh -p 10425 root@195.228.206.225
```

## Session Management

```bash
# Start with session name
hashcat -m 22100 -w 3 hash.txt wordlist.txt --session=bitlocker1

# Resume later
hashcat --restore --session=bitlocker1

# Check status
hashcat --session=bitlocker1 --status
```

## When Password is Found

1. Check potfile: `cat ~/.local/share/hashcat/hashcat.potfile`
2. The password appears after the colon in the hash
3. Use on Windows PC or with dislocker on Linux to decrypt
