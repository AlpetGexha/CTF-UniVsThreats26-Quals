# Irondrop

**Point: 494**

A decommissioned space relay is still forwarding “secure” command traffic through a hardened Android client.
The app is packed with anti-root and anti-instrumentation checks, and it speaks a custom binary protocol over raw TCP.

Your mission: reverse the client, reproduce the protocol logic, gain privileged access to the relay inbox, and extract the classified transmission
The app doesn't run in unsafe environments.

# Solution

## 3) IronDrop

**Recon**
App communicated over raw TCP using a custom binary protocol. Frames were structured as: `cmd (1 byte) | length (2-byte little-endian) | payload`. Mapped out the main commands:

- `0x01/0x02/0x03/0x04` — handshake, challenge, login proof, session
- `0x10/0x11` — list inbox / inbox payload
- `0x20/0x21` — read message by ID / message payload

**Reversing the login proof**
The native function at offset `0x18ec0` handled auth. It builds a proof like this:

- If password length ≤ 255: `h1 = SHA256(challenge XOR SHA256(password))`
- If password length > 255: `h1 = SHA256((0x42 × 32 bytes) || challenge)`
- Then: `core = u8(len(username)) || username || h1`
- Then: `msg = challenge || core || "IRONDROPv2"`
- Then: `h2 = SHA256(K1_CONST || msg)`, `h3 = SHA256(K2_CONST || h2)`
- Final proof sent to server: `core || h3[:16]`

**The bug**
Username length is cast to a single unsigned byte before being serialized. A 256-character username wraps to `0x00`. Pairing that with a 300-character password (to force the long-password branch) produced a proof the server accepted with elevated privileges instead of a guest session.

**Exploit**
Sent login with `username = "A" × 256` and `password = "A" × 300`, got a privileged session, then used `0x10` to list the inbox and `0x20` to read each message until the flag appeared.

**Root cause:** Integer overflow on username length + an alternate crypto branch combined to trick the server into granting higher access than intended.

**Flag:** `UVT{2d9734481e93a68cdd560f2cf4833bbde20e21850361587a62cb7f9ed661dda9}`
