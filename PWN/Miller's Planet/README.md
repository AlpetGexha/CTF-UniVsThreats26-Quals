# Miller's Planet (PWN) - Short Write-up

## Vulnerability

- `vuln()` reads input with `gets()` into a stack buffer when the provided size is `<= 0x100`.
- Stack canary is disabled and PIE is off, so RIP can be reliably overwritten with static addresses.
- The binary also has a useful sequence at `0x401249`: `mov rdi, rax; call system; ...`.

## Exploit Idea

1. Send `1` as the first size to enter the stack-input branch and trigger a classic stack overflow.
2. Overwrite RIP with:
   `ret (0x401164) -> vuln (0x4013a0) -> mov rdi, rax; call system (0x401249) -> fake rbp -> main re-entry (0x40146f)`.
3. During the second `vuln` call, send `300` so input is stored on heap, then send the command string.
4. `gets()` returns the heap pointer in `RAX`, gadget moves it into `RDI`, and `system(command)` executes.

## Run

```bash
python solve.py --host 194.102.62.175 --port 28351
```

## Flag

`UVT{wh0_n33d5_10_stdfile_0_l0ck_wh3n_y0u_hav3_r0p_bWlsbGVyIHMgcGxhbmV0IGlzIGNyYXp5}`
