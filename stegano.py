#!/usr/bin/env python3

import random
import hashlib
import itertools

import PIL.Image
from bitstring import pack, BitStream, ReadError


def format_message(text:bytes)->BitStream :
    return pack("bytes:64, ue, bytes",
                hashlib.sha512(text).digest(),
                len(text),
                text,
                )

def pad_with_noise(text:BitStream, tgtlen:int)-> BitStream :
    """Raises ValueError when tgtlen < len(text)."""
    tgtlen -= len(text)
    bits = BitStream(
        length=tgtlen,
        uint=random.getrandbits(tgtlen),
        )
    return text + bits

def unformat_message(text:BitStream)->bytes :
    """Raises ValueError if the message has been tampered with."""
    try :
        sha, len = text.readlist("bytes:64, ue")
        message = text.read(f"bytes:{len}")
    except ReadError as e :
        raise ValueError("No valid message found — read error.") from e
    if hashlib.sha512(message).digest() != sha :
        raise ValueError("No valid message found — SHA mismatch.")
    return message


def hide(text:bytes, image:PIL.Image.Image)->None :
    imgdata = image.getdata()
    text = pad_with_noise(format_message(text), len(imgdata))
    outseq = (
        b | char & b
        for b, char in zip(text, itertools.chain.from_iterable(imgdata))
    )
    bundled = tuple(zip(*(iter(outseq),)*imgdata.bands))
    image.putdata(bundled)

def show(image:PIL.Image.Image)->bytes :
    bs = BitStream(p&1 for p in itertools.chain.from_iterable(image.getdata()))
    return unformat_message(bs)
