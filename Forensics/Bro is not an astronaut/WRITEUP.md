# ASTRA-9 USB Forensics Write-up

**50 points**

While we were scouring through space in our spaceship, conquering through the stars and planets, our team found A LONE USB STICK!
FLOATING THROUGH SPACE
INTACT!!!
WHY?!?!
HOW?!?!!?
HOW IS THAT POSSIBLE?!?!?!

Anyway...

We have found this USB stick (how) that seems to contain some logs of a long lost spaceship that may have been destroyed. The USB stick seems to have been made with a material that we do know of, but its contents are intact, although it seems data is either corrupted, deleted or encrypted. Someone wanted to get rid of it...
I wonder why🤔

Find out what happened here and retrieve the useful information

## 1) Parse GPT and Locate Partitions

The image has GPT (`EFI PART`) and two partitions:

1. `ASTRA9_USER` (FAT32, live files)
2. `ASTRA9_CACHE` (ext4, deleted artifacts)

## 2) Read Live Files from FAT32

- `/logs/crew_log.txt`
- `/nav.bc`
- `/payload.enc`
- `/readme.txt`

Important clues:

- Crew log gives token prefix: `ASTRA9-`
- Crew log + debrief mention encrypted telemetry fragments in cache
- Debrief states:
  - fragment format uses TLM header
  - sequence field is at offset 4
  - XOR key is in `diag_key.bin`
  - reassemble in sequence order

## 3) Recover Deleted ext4 Files

The script parses ext4 directly and recovers deleted regular files (`links==0`, `dtime!=0`).

Recovered critical inodes:

- `inode 20`: 16-byte high-entropy blob (`diag_key.bin` candidate)
- `inode 21..31`: `TLM` fragments with sequence values
- `inode 18`: `BRO-1337`
- `inode 17`: 32-byte seed candidate (used by payload decoy path)

## 4) Reassemble TLM Alpha/Bravo/Charlie (Real Flag Path)

The corrected solver does:

1. Select TLM fragments with sequence `1, 2, 3` (alpha/bravo/charlie).
2. Read declared per-fragment length from header bytes `[5:7]` (little-endian).
3. XOR candidate windows in each fragment body using `inode 20` as key.
4. Score windows for flag-like charset and boundary checks:
   - seq 1 should begin with `UVT{`
   - seq 3 should end with `}`
5. Pick best window per fragment and concatenate in sequence order.

Recovered parts:

- seq1: `UVT{d0nt_k33p_d1G`
- seq2: `G1in_U_sur3ly_w0N`
- seq3: `t_F1nD_aNythng_:)}`

Concatenated real flag:

- `UVT{d0nt_k33p_d1GG1in_U_sur3ly_w0Nt_F1nD_aNythng_:)}`

## 5) Payload Path (Decoy)

`airlockauth` logic is still valid:

1. `h1 = SHA256(nav.bc)`
2. `h2 = SHA256(seed32 || token || h1)`
3. `payload.enc XOR h2`

With `ASTRA9-BRO-1337` + inode 17 seed, this decrypts to:

- `UVT{S0m3_s3cR3tZ_4r_nVr_m3Ant_t0_B_SHRD}`

This looks like a flag but is a decoy message.

## Final

Use the telemetry-reassembled output:

- `UVT{d0nt_k33p_d1GG1in_U_sur3ly_w0Nt_F1nD_aNythng_:)}`
