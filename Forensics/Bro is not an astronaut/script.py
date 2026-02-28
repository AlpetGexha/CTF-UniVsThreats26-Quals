from __future__ import annotations

import argparse
from pathlib import Path


def xor_repeat(data: bytes, key: bytes) -> bytes:
    return bytes(data[i] ^ key[i % len(key)] for i in range(len(data)))


def is_printable_ascii(data: bytes) -> bool:
    return all(32 <= b < 127 for b in data)


def recover_flag(p2_dir: Path) -> str:
    key = (p2_dir / "inode_20.bin").read_bytes()
    parts: dict[int, str] = {}

    for inode in sorted(p2_dir.glob("inode_*.bin")):
        blob = inode.read_bytes()
        if len(blob) < 8 or not blob.startswith(b"TLM\x01"):
            continue

        seq = blob[4]
        if seq not in (1, 2, 3):
            continue

        frag_len = int.from_bytes(blob[5:7], "little")
        body = blob[7:]
        if frag_len <= 0 or frag_len > len(body):
            continue

        windows = [body[i : i + frag_len] for i in range(len(body) - frag_len + 1)]
        plains = [xor_repeat(w, key) for w in windows]
        plains = [p for p in plains if is_printable_ascii(p)]

        if seq == 1:
            plains = [p for p in plains if p.startswith(b"UVT{")]
        elif seq == 3:
            plains = [p for p in plains if p.endswith(b"}")]

        if len(plains) == 1:
            parts[seq] = plains[0].decode("ascii")

    return "".join(parts[i] for i in (1, 2, 3))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Minimal solver from extracted ext4 deleted files"
    )
    parser.add_argument(
        "--p2-dir",
        default=str(Path(__file__).resolve().parent / "extracted" / "p2_recovered"),
        help="Path to recovered deleted inode files (default: ./extracted/p2_recovered)",
    )
    args = parser.parse_args()

    flag = recover_flag(Path(args.p2_dir))
    if not (flag.startswith("UVT{") and flag.endswith("}")):
        raise SystemExit("Could not recover a valid flag")

    print(flag)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
