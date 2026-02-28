# Vault

VaultDrop is an orbital vault client, used by pilots to sync encrypted manifests from a remote station node.
A breach alert reports that one docked client can query more than it should, and command suspects privilege escalation issues.
The app doesn't run in unsafe environments.

## Solution

## 1) Vault

**Recon**
Started by poking the live API — health check, register, login, file listing. Nothing unusual, so I moved on to the APK.

**Reversing**
Decompiled the app and found it was making JNI calls into native code. Three functions stood out:

- `getAppJwtSecret` — the one that mattered
- `decryptConfig`
- `getDbPassphrase`

Inside `getAppJwtSecret`, the app builds a 48-byte buffer: the first 32 bytes are a hardcoded seed pulled from the binary's read-only data section, and the last 16 bytes are the literal string `vaultdrop.jwt.v2`. It then SHA256s the whole thing and uses the hex output as the JWT signing secret.

**Extracted seed:**

```
1ec2a7b1be9e59fa7a0ff354f12ac8d3a1e646a923cbe5f84e91ac5a0b23eccf
```

**Derived secret:**

```
4536ecd6d1c79c770306392bc7e20b0045437682694d3db5ab77220b8b5d76db
```

**Exploit**
Registered a real user (the server required `sub` to match an existing account), then forged an HS256 JWT with `role=admin`. Sent it to `GET /api/admin/flag` and got the flag.

**Root cause:** The JWT signing key was fully recoverable from the app binary.

**Flag:** `UVT{bbc14e49545f9781161c415081aaac03709fa9f2dcdda458daee0d8c0ba8f9cf}`
