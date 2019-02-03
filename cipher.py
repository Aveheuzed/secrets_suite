#!/usr/bin/env python3
import hashlib

"""Hand-made cipher function. Expected to be pretty safe,
as long as HASHFUNC is know safe and BLOCK_SIZE long enough"""

HASHFUNC = hashlib.sha256
BLOCK_SIZE = 16

def _kiter(key:bytes):
    # need an iterator bc we don't know string's length in advance
    """Iterates on the key : hashes the key (using HASHFUNC), then yields the beginning of the hash.
    The full hash is used as subsequent key. Re-hashes after BLOCK_SIZE bytes yielded.
    yields : int"""
    while True :
        key = HASHFUNC(key).digest()
        yield from key[:BLOCK_SIZE]

def cipher(string:bytes, key:bytes):
    """Kind of Vernam mask : xors the text with the key hashed n times (as yielded by _kiter)
    yields : int"""
    return bytes(s^b for s,b in zip(string, _kiter(key)))

decipher = cipher
