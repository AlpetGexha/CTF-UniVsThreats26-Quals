# Starfield Relay

**Point: 132**
You'll reach the flag no matter what it takes, right?

## Solution

- `main` loads an embedded custom Lua 5.5-like chunk from `.data` (`unk_6302E0`, size `dword_6302C0 = 9,742,391`) and executes it.
- In `sub_405800`, every runtime error updates a counter. At each `0x111088`-th hit, one flag byte is emitted:
  - `collapsed = xor(all 8 bytes of thrown 64-bit value)`
  - `flag[i] = byte_4227E0[i] ^ collapsed`
- `byte_4227E0` starts at `0x4227e0`:
  - `64 0d ae f1 be 1f 6c f5 38 01 f3 e5 07 e0 98 6d f4 fd 4e 20 00 fd 46 df c4 fa 0d 4d c2 ac ...`
- Brute-running was intentionally slow, so I instrumented early throws and derived the exact recurrence for thrown values:
  - `x1 = 0x1fff000`
  - `x(n+1) = splitmix64(x(n) + 0x9E3779B97F4A7C15)`
  - `splitmix64(z) = ((z ^ (z>>30)) * 0xBF58476D1CE4E5B9; (z ^ (z>>27)) * 0x94D049BB133111EB; z ^ (z>>31)) mod 2^64`
- Evaluating this at indices `n = k * 0x111088` and XORing with the key bytes yields:
  - `UVT{R3turn_8y_Thr0w_Del1v3r3r}`

# Flag

`UVT{R3turn_8y_Thr0w_Del1v3r3r}`
