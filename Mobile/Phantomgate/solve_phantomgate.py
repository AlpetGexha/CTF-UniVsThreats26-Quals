#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import hmac
import os
import struct
import time
from typing import Iterable

import requests

ADMIN_TOTP_KEY = bytes.fromhex("a9a4072ac55133f0b39ddbd6261a61b5d4d71df2")
GLOBAL_KEY = bytes.fromhex("f38a1c67bb42e9053dc8a7519f2e764b18d365ae7c0f9238e4b72a5cd981f643")
BASE_URL = "http://194.102.62.175:24041"
UID = 1000
TIMEOUT = 8.0


def hotp(secret: bytes, counter: int) -> int:
    mac = hmac.new(secret, counter.to_bytes(8, "big"), hashlib.sha1).digest()
    off = mac[-1] & 0x0F
    code = struct.unpack(">I", mac[off : off + 4])[0] & 0x7FFFFFFF
    return code % 1_000_000


def totp(secret: bytes, unix_ts: int, step: int = 30) -> int:
    return hotp(secret, unix_ts // step)


def _rotl32(x: int, n: int) -> int:
    return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF


def _quarter_round(st: list[int], a: int, b: int, c: int, d: int) -> None:
    st[a] = (st[a] + st[b]) & 0xFFFFFFFF
    st[d] ^= st[a]
    st[d] = _rotl32(st[d], 16)

    st[c] = (st[c] + st[d]) & 0xFFFFFFFF
    st[b] ^= st[c]
    st[b] = _rotl32(st[b], 12)

    st[a] = (st[a] + st[b]) & 0xFFFFFFFF
    st[d] ^= st[a]
    st[d] = _rotl32(st[d], 8)

    st[c] = (st[c] + st[d]) & 0xFFFFFFFF
    st[b] ^= st[c]
    st[b] = _rotl32(st[b], 7)


def chacha20_block(key32: bytes, counter: int, nonce12: bytes) -> bytes:
    if len(key32) != 32:
        raise ValueError("key must be 32 bytes")
    if len(nonce12) != 12:
        raise ValueError("nonce must be 12 bytes")

    constants = [0x61707865, 0x3320646E, 0x79622D32, 0x6B206574]
    key_words = list(struct.unpack("<8I", key32))
    nonce_words = list(struct.unpack("<3I", nonce12))

    st = constants + key_words + [counter & 0xFFFFFFFF] + nonce_words
    wrk = st[:]

    for _ in range(10):
        _quarter_round(wrk, 0, 4, 8, 12)
        _quarter_round(wrk, 1, 5, 9, 13)
        _quarter_round(wrk, 2, 6, 10, 14)
        _quarter_round(wrk, 3, 7, 11, 15)

        _quarter_round(wrk, 0, 5, 10, 15)
        _quarter_round(wrk, 1, 6, 11, 12)
        _quarter_round(wrk, 2, 7, 8, 13)
        _quarter_round(wrk, 3, 4, 9, 14)

    out = [(wrk[i] + st[i]) & 0xFFFFFFFF for i in range(16)]
    return struct.pack("<16I", *out)


def build_token(otp6: str, uid: int, nonce12: bytes) -> str:
    derived_key = hashlib.sha256(GLOBAL_KEY[:16] + uid.to_bytes(4, "little", signed=False)).digest()
    keystream = chacha20_block(derived_key, counter=1, nonce12=nonce12)
    otp_bytes = otp6.encode()
    ct = bytes(a ^ b for a, b in zip(otp_bytes, keystream[: len(otp_bytes)]))
    tag = hashlib.sha256(ct + derived_key).digest()[:16]
    return (ct + tag).hex()


def extract_server_ts(obj: dict[str, object]) -> int:
    for k in ("server_time", "time", "timestamp", "ts", "now"):
        v = obj.get(k)
        if isinstance(v, int):
            return v
        if isinstance(v, float):
            return int(v)
        if isinstance(v, str) and v.isdigit():
            return int(v)
    return int(time.time())


def slot_times(now: int, step: int, window: int = 2) -> Iterable[int]:
    for k in range(-window, window + 1):
        yield now + (k * step)


def run(base: str, uid: int = 1000, timeout: float = 8.0) -> int:
    base = base.rstrip("/")
    s = requests.Session()

    t = s.get(f"{base}/api/time", timeout=timeout)
    t.raise_for_status()
    obj = t.json() if t.headers.get("content-type", "").startswith("application/json") else {}

    now = extract_server_ts(obj if isinstance(obj, dict) else {})
    step = int(obj.get("totp_step", 30)) if isinstance(obj, dict) else 30

    for ts in slot_times(now, step, window=3):
        otp = f"{totp(ADMIN_TOTP_KEY, ts, step=step):06d}"
        nonce = os.urandom(12)
        token = build_token(otp, uid=uid, nonce12=nonce)

        headers = {
            "X-Admin-OTP": otp,
            "X-Admin-Token": token,
            "X-Admin-Nonce": nonce.hex(),
            "X-Caller-UID": str(uid),
        }
        r = s.get(f"{base}/api/admin/flag", headers=headers, timeout=timeout)
        if "UVT{" in r.text or "flag{" in r.text:
            print(f"[+] success ts={ts} otp={otp}")
            print(r.text)
            return 0

    print("[-] no flag in tested window")
    return 1


def main() -> int:
    return run(BASE_URL, uid=UID, timeout=TIMEOUT)


if __name__ == "__main__":
    raise SystemExit(main())
