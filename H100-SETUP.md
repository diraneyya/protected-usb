# BitLocker Cracking on H100 GPU - Setup Guide

## Expected Performance

| GPU | BitLocker Speed (estimated) |
|-----|----------------------------|
| H100 | ~50,000 - 80,000 H/s |
| Your M2 Pro | 469 H/s |
| **Speedup** | **~100-170x faster** |

At 60,000 H/s, the rockyou wordlist (14M passwords) completes in **~4 minutes**.

---

## Quick Start (Copy-Paste Ready)

### 1. Connect to your H100 instance

```bash
ssh user@your-h100-instance
```

### 2. One-liner setup (Ubuntu/Debian)

```bash
# Update and install hashcat + NVIDIA drivers
sudo apt update && sudo apt install -y hashcat nvidia-driver-535 nvidia-cuda-toolkit

# Verify GPU is detected
nvidia-smi
hashcat -I
```

### 3. Create the hash file

```bash
mkdir -p ~/bitlocker && cat > ~/bitlocker/hash.txt << 'EOF'
$bitlocker$0$16$b3b78555e45367d2d735588ffe89ce85$1048576$12$90e2969ca76cd50103000000$60$692c659b722d52df34acaf73c8f52f15e34a1d6267f8840e3fc93f1c488ab800ed1e0128f701eced9dd1116ace6c42144ed70825b6cf7f01202424f3
EOF
```

### 4. Download wordlists

```bash
cd ~/bitlocker

# Rockyou (14M passwords, ~140MB)
wget -q https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt

# Optional: Larger wordlists
# wget https://download.weakpass.com/wordlists/90/weakpass_2.txt.gz && gunzip weakpass_2.txt.gz
```

### 5. Run the attack

```bash
# Dictionary attack with rockyou
hashcat -m 22100 -d 1 -w 3 ~/bitlocker/hash.txt ~/bitlocker/rockyou.txt

# With rules (more thorough, 10-100x more candidates)
hashcat -m 22100 -d 1 -w 3 ~/bitlocker/hash.txt ~/bitlocker/rockyou.txt -r /usr/share/hashcat/rules/best64.rule
```

---

## Detailed Setup

### For Ubuntu 22.04/24.04 LTS

```bash
# 1. Install NVIDIA drivers (if not pre-installed)
sudo apt update
sudo apt install -y nvidia-driver-535

# 2. Reboot if driver was just installed
sudo reboot

# 3. Verify GPU
nvidia-smi

# 4. Install hashcat
sudo apt install -y hashcat

# 5. Verify hashcat sees the GPU
hashcat -I
```

### For Cloud Instances (Lambda Labs, Vast.ai, RunPod)

Most come with drivers pre-installed. Just:

```bash
sudo apt update && sudo apt install -y hashcat wget
hashcat -I  # Should show H100
```

### For Docker (if preferred)

```bash
docker run --gpus all -it --rm \
  -v ~/bitlocker:/data \
  dizcza/docker-hashcat:latest \
  hashcat -m 22100 -d 1 -w 3 /data/hash.txt /data/rockyou.txt
```

---

## Attack Commands

### Benchmark first (verify H100 performance)

```bash
hashcat -b -m 22100
```

Expected output: `Speed.#1: ~50000-80000 H/s`

### Dictionary Attack (Start Here)

```bash
# Basic rockyou attack (~4 minutes)
hashcat -m 22100 -d 1 -w 3 hash.txt rockyou.txt

# With best64 rules (~6 hours, very thorough)
hashcat -m 22100 -d 1 -w 3 hash.txt rockyou.txt -r /usr/share/hashcat/rules/best64.rule

# With dive rules (more aggressive mutations)
hashcat -m 22100 -d 1 -w 3 hash.txt rockyou.txt -r /usr/share/hashcat/rules/dive.rule
```

### Brute Force Attacks

```bash
# 6 characters lowercase (a-z) - ~2 minutes
hashcat -m 22100 -a 3 -d 1 -w 3 hash.txt ?l?l?l?l?l?l

# 6 characters alphanumeric (a-z, 0-9) - ~20 minutes
hashcat -m 22100 -a 3 -d 1 -w 3 hash.txt ?h?h?h?h?h?h

# 7 characters lowercase - ~1 hour
hashcat -m 22100 -a 3 -d 1 -w 3 hash.txt ?l?l?l?l?l?l?l

# 8 characters lowercase - ~26 hours
hashcat -m 22100 -a 3 -d 1 -w 3 hash.txt ?l?l?l?l?l?l?l?l
```

### Mask Attacks (Pattern-Based)

```bash
# Word + 4 digits (e.g., password1234)
hashcat -m 22100 -a 6 -d 1 -w 3 hash.txt rockyou.txt ?d?d?d?d

# Capital + lowercase + digits (e.g., Password123)
hashcat -m 22100 -a 3 -d 1 -w 3 hash.txt ?u?l?l?l?l?l?l?d?d?d

# Year suffix (e.g., something2019)
hashcat -m 22100 -a 6 -d 1 -w 3 hash.txt rockyou.txt 201?d
hashcat -m 22100 -a 6 -d 1 -w 3 hash.txt rockyou.txt 202?d
```

### Hybrid Attacks

```bash
# Wordlist + append 1-4 digits
hashcat -m 22100 -a 6 -d 1 -w 3 hash.txt rockyou.txt ?d
hashcat -m 22100 -a 6 -d 1 -w 3 hash.txt rockyou.txt ?d?d
hashcat -m 22100 -a 6 -d 1 -w 3 hash.txt rockyou.txt ?d?d?d
hashcat -m 22100 -a 6 -d 1 -w 3 hash.txt rockyou.txt ?d?d?d?d

# Prepend digits + wordlist
hashcat -m 22100 -a 7 -d 1 -w 3 hash.txt ?d?d?d?d rockyou.txt
```

---

## Hashcat Flags Explained

| Flag | Meaning |
|------|---------|
| `-m 22100` | BitLocker hash mode |
| `-a 0` | Dictionary attack (default) |
| `-a 3` | Brute force/mask attack |
| `-a 6` | Hybrid: wordlist + mask |
| `-a 7` | Hybrid: mask + wordlist |
| `-d 1` | Use device #1 (GPU) |
| `-w 3` | Workload: high (fastest) |
| `-r file.rule` | Apply rule file |
| `--session=name` | Name session for restore |
| `--restore` | Resume previous session |
| `-o found.txt` | Output found passwords to file |

---

## Time Estimates (H100 @ 60,000 H/s)

| Attack | Keyspace | Time |
|--------|----------|------|
| Rockyou (14M) | 14,344,391 | ~4 minutes |
| Rockyou + best64 | ~1.1 billion | ~5 hours |
| 6-char lowercase | 308,915,776 | ~1.4 hours |
| 6-char alphanumeric | 2,176,782,336 | ~10 hours |
| 7-char lowercase | 8,031,810,176 | ~37 hours |
| 8-char lowercase | 208,827,064,576 | ~40 days |

---

## Recommended Attack Order

Run these in order, stopping when password is found:

```bash
# 1. Quick wins - common passwords (~4 min)
hashcat -m 22100 -d 1 -w 3 hash.txt rockyou.txt

# 2. Common passwords with mutations (~5 hrs)
hashcat -m 22100 -d 1 -w 3 hash.txt rockyou.txt -r /usr/share/hashcat/rules/best64.rule

# 3. Short brute force (~1.5 hrs)
hashcat -m 22100 -a 3 -d 1 -w 3 hash.txt ?l?l?l?l?l?l

# 4. Alphanumeric short (~10 hrs)
hashcat -m 22100 -a 3 -d 1 -w 3 hash.txt ?h?h?h?h?h?h

# 5. 7-char lowercase (~37 hrs)
hashcat -m 22100 -a 3 -d 1 -w 3 hash.txt ?l?l?l?l?l?l?l
```

---

## Session Management (Important for Long Runs)

```bash
# Start with session name
hashcat -m 22100 -d 1 -w 3 hash.txt rockyou.txt --session=bitlocker1

# Check status (press 's' during run)
# Pause (press 'p')
# Quit and save (press 'q')

# Resume later
hashcat --restore --session=bitlocker1

# List sessions
ls ~/.local/share/hashcat/sessions/
```

---

## When Password is Found

Hashcat will display:

```
$bitlocker$0$16$...:FOUND_PASSWORD

Session..........: hashcat
Status...........: Cracked
```

The password appears after the colon.

### Show found password again:

```bash
hashcat -m 22100 hash.txt --show
```

---

## Transfer Results Back to Mac

```bash
# On H100 instance - if password found
hashcat -m 22100 hash.txt --show > ~/bitlocker/result.txt

# From your Mac
scp user@h100-instance:~/bitlocker/result.txt ~/bitlocker-recovery/
```

---

## Using Found Password

Once you have the password, on your Mac:

### Option A: Use Windows (easiest)
Plug drive into any Windows PC, enter password when prompted.

### Option B: Use dislocker on Linux

```bash
# Install dislocker
sudo apt install dislocker

# Decrypt (creates virtual device)
sudo dislocker -u -V /dev/sdX -- /mnt/bitlocker
# Enter password when prompted

# Mount the decrypted volume
sudo mount -o loop /mnt/bitlocker/dislocker-file /mnt/data

# Access files
ls /mnt/data
```

### Option C: Commercial Mac software
M3 BitLocker Loader, iBoysoft, etc. - enter password in their UI.

---

## Troubleshooting

### "No devices found"
```bash
# Check NVIDIA driver
nvidia-smi

# If no output, install driver
sudo apt install nvidia-driver-535
sudo reboot
```

### "CUDA SDK not found"
```bash
sudo apt install nvidia-cuda-toolkit
```

### Hashcat shows only CPU
```bash
# Force GPU
hashcat -m 22100 -D 2 hash.txt wordlist.txt
```

### Out of memory
```bash
# Reduce workload
hashcat -m 22100 -w 2 hash.txt wordlist.txt
```

---

## Cost Estimate

| Provider | H100 Cost | Rockyou Attack | 24hr Heavy Attack |
|----------|-----------|----------------|-------------------|
| Lambda Labs | ~$2.50/hr | ~$0.20 | ~$60 |
| Vast.ai | ~$2-4/hr | ~$0.15-0.30 | ~$48-96 |
| RunPod | ~$2.50/hr | ~$0.20 | ~$60 |
| AWS p5 | ~$30/hr | ~$2.50 | ~$720 |

For a thorough attack (rockyou + rules + 6-char brute force): ~$10-20 on budget providers.

---

## Arabic Password Attacks

If the password may contain Arabic characters, use the custom mask file approach.

### Arabic Character Set (36 letters)

```
ابتثجحخدذرزسشصضطظعغفقكلمنهوي   (28 base letters)
أإآئةؤءى                        (8 additional forms)
```

### Create the Arabic Mask File

```bash
cat > ~/bitlocker/arabic_attack.hcmask << 'EOF'
# Arabic charset: 28 base + أ إ آ ئ ة ؤ ء ى = 36 letters
# ?1 = all Arabic letters

# 4-letter Arabic password (no numbers)
ابتثجحخدذرزسشصضطظعغفقكلمنهويأإآئةؤءى,?1?1?1?1

# 4-letter Arabic + 1 digit
ابتثجحخدذرزسشصضطظعغفقكلمنهويأإآئةؤءى,?1?1?1?1?d

# 4-letter Arabic + 2 digits
ابتثجحخدذرزسشصضطظعغفقكلمنهويأإآئةؤءى,?1?1?1?1?d?d

# 4-letter Arabic + 3 digits
ابتثجحخدذرزسشصضطظعغفقكلمنهويأإآئةؤءى,?1?1?1?1?d?d?d

# 4-letter Arabic + 4 digits (includes years like 2019)
ابتثجحخدذرزسشصضطظعغفقكلمنهويأإآئةؤءى,?1?1?1?1?d?d?d?d

# 5-letter Arabic password (no numbers)
ابتثجحخدذرزسشصضطظعغفقكلمنهويأإآئةؤءى,?1?1?1?1?1

# 5-letter Arabic + 1 digit
ابتثجحخدذرزسشصضطظعغفقكلمنهويأإآئةؤءى,?1?1?1?1?1?d

# 5-letter Arabic + 2 digits
ابتثجحخدذرزسشصضطظعغفقكلمنهويأإآئةؤءى,?1?1?1?1?1?d?d

# 5-letter Arabic + 3 digits
ابتثجحخدذرزسشصضطظعغفقكلمنهويأإآئةؤءى,?1?1?1?1?1?d?d?d

# 5-letter Arabic + 4 digits (includes years)
ابتثجحخدذرزسشصضطظعغفقكلمنهويأإآئةؤءى,?1?1?1?1?1?d?d?d?d

# 4-letter Arabic + @ + 4 digits
ابتثجحخدذرزسشصضطظعغفقكلمنهويأإآئةؤءى,?1?1?1?1@?d?d?d?d

# 5-letter Arabic + @ + 4 digits
ابتثجحخدذرزسشصضطظعغفقكلمنهويأإآئةؤءى,?1?1?1?1?1@?d?d?d?d

# 6-letter Arabic password (no numbers)
ابتثجحخدذرزسشصضطظعغفقكلمنهويأإآئةؤءى,?1?1?1?1?1?1

# 6-letter Arabic + 2 digits
ابتثجحخدذرزسشصضطظعغفقكلمنهويأإآئةؤءى,?1?1?1?1?1?1?d?d
EOF
```

### Arabic Attack Time Estimates (4x RTX 4090 @ ~60,000 H/s)

| Pattern | Example | Combinations | Time |
|---------|---------|--------------|------|
| 4 Arabic | كلمة | 36^4 = 1.7M | ~30 sec |
| 4 Arabic + 1 digit | كلمة1 | 17M | ~5 min |
| 4 Arabic + 2 digits | كلمة12 | 168M | ~45 min |
| 4 Arabic + 3 digits | كلمة123 | 1.7B | ~8 hrs |
| 4 Arabic + 4 digits | كلمة2019 | 17B | ~3 days |
| 5 Arabic | كلمةس | 36^5 = 60M | ~17 min |
| 5 Arabic + 4 digits | محمد2019 | 604B | ~4 days |
| 6 Arabic | كلمةسر | 36^6 = 2.2B | ~10 hrs |

### Run the Arabic Attack

```bash
# Upload mask file to server (from Mac)
scp -P <port> ~/bitlocker-recovery/arabic_attack.hcmask root@<server>:~/bitlocker/

# Run attack with mask file
hashcat -m 22100 -a 3 -w 3 ~/bitlocker/hash.txt ~/bitlocker/arabic_attack.hcmask --session=arabic1

# Use all GPUs (remove -d flag or specify all)
hashcat -m 22100 -a 3 -w 3 ~/bitlocker/hash.txt ~/bitlocker/arabic_attack.hcmask -d 1,2,3,4 --session=arabic1
```

### Understanding the Mask File Format

Each line in `.hcmask` file:
```
<charset_definition>,<mask_pattern>
```

| Part | Meaning |
|------|---------|
| `ابتثجحخدذرزسشصضطظعغفقكلمنهويأإآئةؤءى` | Defines `?1` = any of these 36 Arabic letters |
| `,` | Separator |
| `?1?1?1?1` | 4 positions, each using charset 1 (Arabic) |
| `?d` | One digit (0-9) |
| `@` | Literal @ character |

### Specific Year Patterns

If you suspect the password ends with a specific year:

```bash
# 5 Arabic letters + 2019 (encryption year)
hashcat -m 22100 -a 3 -w 3 hash.txt \
  -1 "ابتثجحخدذرزسشصضطظعغفقكلمنهويأإآئةؤءى" \
  ?1?1?1?1?12019

# 5 Arabic letters + years 2015-2025
for year in 2015 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025; do
  hashcat -m 22100 -a 3 -w 3 hash.txt \
    -1 "ابتثجحخدذرزسشصضطظعغفقكلمنهويأإآئةؤءى" \
    "?1?1?1?1?1$year" --session=year_$year
done
```

### Mixed Arabic + English Attacks

Create a hybrid wordlist:

```bash
cat > ~/bitlocker/mixed_words.txt << 'EOF'
كلمة
كلمةسر
مرحبا
password
admin
محمد
احمد
علي
سر
باسورد
EOF

# Dictionary + digits
hashcat -m 22100 -a 6 -w 3 hash.txt ~/bitlocker/mixed_words.txt ?d?d?d?d
```

---

## Multi-GPU Usage

When using multiple GPUs, **do not use `-d 1`** (single device). Instead:

```bash
# Use ALL available GPUs (recommended)
hashcat -m 22100 -w 3 hash.txt wordlist.txt

# Or explicitly specify multiple devices
hashcat -m 22100 -w 3 hash.txt wordlist.txt -d 1,2,3,4

# Check GPU utilization during attack
nvidia-smi -l 1  # Updates every 1 second
```

### Verify All GPUs Are Working

```bash
# Should show ~100% utilization on all GPUs
nvidia-smi --query-gpu=index,utilization.gpu,temperature.gpu,power.draw --format=csv
```

Expected output:
```
index, utilization.gpu [%], temperature.gpu, power.draw [W]
0, 100 %, 65, 350 W
1, 100 %, 68, 380 W
2, 100 %, 67, 375 W
3, 100 %, 70, 390 W
```

---

## Summary Checklist

- [ ] SSH into GPU instance
- [ ] Verify GPU: `nvidia-smi`
- [ ] Install hashcat: `sudo apt install hashcat` (or pip install for newer version)
- [ ] Verify hashcat sees GPU: `hashcat -I`
- [ ] Create hash file (copy from above)
- [ ] Download rockyou.txt
- [ ] Run benchmark: `hashcat -b -m 22100`
- [ ] Start attack: `hashcat -m 22100 -w 3 hash.txt rockyou.txt` (no `-d 1` for multi-GPU)
- [ ] For Arabic: upload mask file and run with `-a 3`
- [ ] Monitor: `nvidia-smi` to verify all GPUs at 100%
- [ ] If found, copy password and decrypt drive
