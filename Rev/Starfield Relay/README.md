# Starfield Relay

**Point: 50**

A recovered spacecraft utility binary is believed to validate a multi-part unlock phrase.
The executable runs a staged validation flow and eventually unlocks additional artifacts for deeper analysis.
Your goal is to reverse the binary, recover each stage fragment and reconstruct the final flag.

This crackme is a staged builder: each stage validates a fragment and appends it to a running string. After stage 10, the concatenation is the flag.

Stage 1

- Prompt: base prefix (4 chars)
- Check is direct `memcmp(..., "UVT{", 4)`.
- Fragment: `UVT{`

Stage 2

- Prompt: 3-char fragment
- Helper function builds expected string directly:
  - bytes: `0x4b 0x72 0x34`
- Fragment: `Kr4`

Stage 3

- Prompt: stage2 token (8 chars)
- Constraint per byte:
  - `7*i + (in[i] ^ (17*i + 109)) + 19 == target[i]`
  - `target = 0xC5E42C25FADC2431` (little-endian bytes)
- Inverting gives:
- Fragment: `st4rG4te`

Stage 4

- Prompt: token (8 chars)
- Constraint per byte:
  - `3*i + (in[i] ^ (-89 - 11*i)) == target[i]`
  - `target = pack("<II", -307768873, 1231567188)`
- Inverting gives:
- Fragment: `pR0b3Z3n`

Stage 5 (no input)

- VM bytecode is decoded and interpreted (`sub_140117D90` + `sub_140118090`).
- VM output is hashed and compared against embedded target.
- Recovered output:
- Fragment: `THEN-`

Stage 6 (payload extraction, no fragment)

- This stage extracts the embedded `stage2` payload and verifies it via `stage2.sha256`.
- It does not require user input and does not contribute a new typed fragment.

Stage 7 (starfield pings)

- File: `stage2/starfield_pings/pings.txt`
- Filter on `ttl=1337`, use `time` as 5-bit symbols.
- Decoder maps are split by symbol parity:
  - even symbols use `map_even_xor52`
  - odd symbols use `map_odd_rev_xor13`
- Decoded fragment:
- Fragment: `uR_pR0b3Z_xTND-`

Stage 8 (logs)

- File: `stage2/logs/system.log`
- Use `subsys="zen"` entries, order by `slot`, XOR `fragx` with key `k`.
- Concatenation gives base64 text:
  - `SV9oMUQzX2luX2wwR3pf`
- Base64 decode:
- Fragment: `I_h1D3_in_l0Gz_`

Stage 9 (void island)

- File: `stage2/void/zen_void.bin`
- Apply key `0x2a` to the correct non-zero island in the valid void range.
- Matching fragment:
- Fragment: `1n_v01D_`

Stage 10 (final)

- Key rule from readme:
  - `key = sum(bytes(stage8_text)) % 256`
- From stage 8:
  - `sum(b"1n_v01D_") % 256 = 0x78`
- Decode the next island with `0x78`:
- Fragment: `iN_ZEN}`

---

Reconstructing the final flag

Concatenate stage fragments in order:

1. UVT{
2. Kr4
3. st4rG4te
4. pR0b3Z3n
5. THEN-
6. uR_pR0b3Z_xTND-
7. I*h1D3_in_l0Gz*
8. 1n*v01D*
9. iN_ZEN}

Result:
UVT{Kr4st4rG4tepR0b3Z3nTHEN-uR_pR0b3Z_xTND-I_h1D3_in_l0Gz_1n_v01D_iN_ZEN}
