# BitLocker Drive Recovery - Analysis Report

**Date:** November 29, 2025
**Drive:** Sony USB 3.0 (16.2 GB)
**Device:** /dev/disk4

---

## Drive Overview

| Property | Value |
|----------|-------|
| Type | BitLocker To Go |
| BitLocker Version | 2 (Windows 7 or later) |
| Encryption | AES-CCM |
| Key Iterations | 1,048,576 (2^20) |
| Encrypted Since | September 16, 2019 |
| Total Encrypted Data | ~15 GB across 4 COV files |

---

## Extracted Hashes

### User Password Hash (Primary Attack Target)

**Fast attack mode (mode 0):**
```
$bitlocker$0$16$b3b78555e45367d2d735588ffe89ce85$1048576$12$90e2969ca76cd50103000000$60$692c659b722d52df34acaf73c8f52f15e34a1d6267f8840e3fc93f1c488ab800ed1e0128f701eced9dd1116ace6c42144ed70825b6cf7f01202424f3
```

**With MAC verification (mode 1, slower, no false positives):**
```
$bitlocker$1$16$b3b78555e45367d2d735588ffe89ce85$1048576$12$90e2969ca76cd50103000000$60$692c659b722d52df34acaf73c8f52f15e34a1d6267f8840e3fc93f1c488ab800ed1e0128f701eced9dd1116ace6c42144ed70825b6cf7f01202424f3
```

### Recovery Password Hash (NOT Practically Crackable)

**Mode 2 (fast):**
```
$bitlocker$2$16$0c62c24a1a1e784865cdb54a40274eff$1048576$12$90e2969ca76cd50106000000$60$75d0e7ecbc11ed83a269b95a1bf345891638ecbcdfd010fa1ff08bb6f12fa52cc46cc58f9b1cd7bf6739b23c0fd881fec8667ff93127e4efdc568e57
```

**Mode 3 (with MAC):**
```
$bitlocker$3$16$0c62c24a1a1e784865cdb54a40274eff$1048576$12$90e2969ca76cd50106000000$60$75d0e7ecbc11ed83a269b95a1bf345891638ecbcdfd010fa1ff08bb6f12fa52cc46cc58f9b1cd7bf6739b23c0fd881fec8667ff93127e4efdc568e57
```

---

## Hash Structure Breakdown

```
$bitlocker$[mode]$[salt_len]$[salt]$[iterations]$[nonce_len]$[nonce]$[data_len]$[mac+vmk]
```

| Field | Value | Meaning |
|-------|-------|---------|
| Mode | 0 or 1 | User password (0=fast, 1=verified) |
| Salt | b3b78555e45367d2d735588ffe89ce85 | 16-byte random salt |
| Iterations | 1048576 | SHA-256 rounds (makes cracking slow) |
| Nonce | 90e2969ca76cd50103000000 | AES-CCM nonce |
| MAC+VMK | 692c659b...202424f3 | Encrypted Volume Master Key |

---

## Cracking Feasibility

### Hardware Performance

| Hardware | Speed (H/s) | Notes |
|----------|-------------|-------|
| Your M2 Pro | ~469 | Current machine |
| RTX 4090 | ~15,000 | Best consumer GPU |
| RTX 3090 | ~10,000 | High-end GPU |
| 8x RTX 4090 | ~120,000 | Multi-GPU rig |
| Cloud (Vast.ai) | Variable | Rent by the hour |

### Time Estimates (at 469 H/s - your M2 Pro)

| Password Type | Keyspace | Time |
|---------------|----------|------|
| 4-char lowercase | 456,976 | ~16 minutes |
| 6-char lowercase | 308,915,776 | ~7.6 days |
| 6-char alphanumeric | 2,176,782,336 | ~53 days |
| 8-char lowercase | 208,827,064,576 | ~14 years |
| 8-char mixed+numbers | 218,340,105,584,896 | ~14,700 years |
| Rockyou wordlist | 14,344,391 | ~8.5 hours |
| Recovery key (48 digits) | 10^48 | Heat death of universe |

### Time Estimates (at 15,000 H/s - RTX 4090)

| Password Type | Time |
|---------------|------|
| 6-char lowercase | ~5.7 hours |
| 6-char alphanumeric | ~40 hours |
| 8-char lowercase | ~160 days |
| Rockyou wordlist | ~16 minutes |

---

## Attack Strategies

### 1. Dictionary Attack (Recommended First)

Best if the password is a common word or phrase.

```bash
# Using hashcat with rockyou.txt
hashcat -m 22100 ~/bitlocker-recovery/user_password_hash.txt rockyou.txt

# Using John the Ripper
john --format=bitlocker ~/bitlocker-recovery/hashes.txt --wordlist=rockyou.txt
```

**Wordlists to try:**
- `rockyou.txt` (14M passwords) - https://github.com/brannondorsey/naive-hashcat/releases
- `SecLists` - https://github.com/danielmiessler/SecLists
- Custom wordlist based on owner's info

### 2. Rule-Based Attack

Applies mutations to dictionary words (Password → p@ssw0rd, password123, etc.)

```bash
hashcat -m 22100 hash.txt wordlist.txt -r best64.rule
```

### 3. Targeted Attack

If you know anything about the password creator:
- Names, dates, pets, locations
- Company name, project names
- Common patterns they use

```bash
# Create custom wordlist
cat > custom.txt << EOF
CompanyName2019
Project123
[pet name][birth year]
EOF

john --format=bitlocker hashes.txt --wordlist=custom.txt
```

### 4. Brute Force (Last Resort)

Only viable for very short passwords.

```bash
# 6-char lowercase
hashcat -m 22100 hash.txt -a 3 ?l?l?l?l?l?l

# 6-char alphanumeric
hashcat -m 22100 hash.txt -a 3 ?a?a?a?a?a?a
```

### 5. Cloud Cracking

Rent GPU power for faster cracking:
- **Vast.ai** - Cheapest, rent individual GPUs
- **AWS p4d instances** - 8x A100 GPUs
- **Google Cloud** - A100/H100 GPUs
- **Hashtopolis** - Distributed cracking

---

## Quick Test Commands

### Test a single password guess:
```bash
echo "your_guess" | john --format=bitlocker ~/bitlocker-recovery/hashes.txt --stdin
```

### Test multiple guesses from file:
```bash
john --format=bitlocker ~/bitlocker-recovery/hashes.txt --wordlist=guesses.txt
```

### Check if already cracked:
```bash
john --show --format=bitlocker ~/bitlocker-recovery/hashes.txt
```

---

## Alternative Recovery Methods

### 1. Find the Recovery Key
The 48-digit recovery key may be stored in:
- Microsoft account (if linked): https://account.microsoft.com/devices/recoverykey
- Active Directory (corporate environments)
- Printed backup
- USB backup key (.BEK file)
- Azure AD (corporate)

### 2. Memory Forensics
If you have a memory dump from when the drive was unlocked:
- Tools: Volatility, Elcomsoft Forensic Disk Decryptor
- The Volume Master Key (VMK) may be extractable

### 3. Professional Data Recovery
Commercial services with specialized hardware:
- Elcomsoft
- Passware
- Ontrack

---

## Files in This Directory

```
~/bitlocker-recovery/
├── README.md              # This file
├── hashes.txt             # All extracted hashes with comments
└── user_password_hash.txt # Just the crackable user password hash
```

---

## Next Steps Decision Tree

```
Do you have any idea what the password might be?
├── Yes → Create targeted wordlist, run dictionary attack
└── No
    ├── Is the password likely simple/common?
    │   ├── Yes → Run rockyou.txt attack (~8 hrs on M2 Pro)
    │   └── No/Unknown
    │       ├── Have access to powerful GPU(s)?
    │       │   ├── Yes → Run extended dictionary + rules attack
    │       │   └── No → Consider cloud GPU rental
    │       └── Is data worth significant expense?
    │           ├── Yes → Professional recovery service
    │           └── No → Best effort with available resources
```

---

## Important Notes

1. **No backdoors exist** - BitLocker encryption is cryptographically sound
2. **Recovery key is uncrackable** - 48 random digits = impossible keyspace
3. **Success depends entirely on password weakness**
4. **This is your data** - Ensure you have legal right to access it

---

## Resources

- [Hashcat BitLocker mode](https://hashcat.net/wiki/doku.php?id=example_hashes) - Mode 22100
- [John the Ripper](https://github.com/openwall/john)
- [BitCracker](https://github.com/e-ago/bitcracker) - GPU-accelerated BitLocker cracker
- [Rockyou wordlist](https://github.com/brannondorsey/naive-hashcat/releases)
- [SecLists](https://github.com/danielmiessler/SecLists)
