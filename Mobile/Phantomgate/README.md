# Phantomgate

**Point: 261**

Deep in the outer-ring stations, PhantomGate protects command access to a classified orbital network.
You intercepted only an Android APK and the remote gateway endpoint. Somewhere inside the app is the path to forge an admin authentication proof and unlock the control channel.
Reverse the client, break the protection layers, and breach the gate before the auth window collapses.
The app doesn't run in unsafe environments.
At some point you will need to get the api system time.

## Solution

**Recon**
`/api/time` leaked server time and confirmed a 30-second TOTP window. `/api/admin/flag` told me exactly what it needed:

- `X-Admin-OTP` — 6-digit code
- `X-Admin-Token` — 44 hex chars
- `X-Admin-Nonce` — 24 hex chars
- `X-Caller-UID`

**Reversing**
The Java layer was just glue — the real logic lived in `libphantom_crypto.so`. Inside I found:

- A hardcoded admin account identifier (`admin_backup`)
- A 20-byte admin TOTP key: `a9a4072ac55133f0b39ddbd6261a61b5d4d71df2`
- A 32-byte global key: `f38a1c67bb42e9053dc8a7519f2e764b18d365ae7c0f9238e4b72a5cd981f643`
- Standard HOTP truncation over HMAC-SHA1, mod 1,000,000 for the OTP

**Token construction** (reverse engineered from native code):

1. `derived_key = SHA256(global_key[:16] || uid_as_le32)`
2. Generate a ChaCha20 keystream (counter=1, your nonce)
3. XOR the 6 OTP bytes with the keystream prefix → 6-byte ciphertext
4. `tag = SHA256(ciphertext || derived_key)[:16]`
5. Final token = ciphertext + tag = 22 bytes = 44 hex chars

**Exploit**
Grabbed server time, computed the OTP for the current slot (±1 for clock skew), generated a nonce, built the token with the above steps, sent all headers together.

**Root cause:** Every piece of the auth puzzle — TOTP seed, token algorithm, crypto keys — was sitting in the app binary.

**Flag:** `UVT{5db27607b1ba5395e8e24be2ab2dad0ef0ccf744b6966be51ef8b58d6583e681}`
