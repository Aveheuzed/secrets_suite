#!/usr/bin/env python3
import itertools
import operator

import PIL.Image

"""Steganography utilities. Hides (or reveals) the message hidden
in the lsb of each pixel of the picture (on each channel)
The length of the message is hidden before it, on FLAG_SIZE bytes
(ending on 8*FLAG_SIZE bytes of picture data)"""

FLAG_SIZE = 4
# size (in bytes) of the start flag, indicating the text's length

BANDS = 3
# number of bands in the picture (3 : R,G,B)

def _titer(text:bytes):
    """Generator splitting bytes into bits, using logical operators.
    yield : int (0 or 1)"""
    masks = [(1<<x, x) for x in range(7,-1,-1)]
    for t in text :
        for m, s in masks :
            yield (t&m)>>s
    # 10110101 => 00000100 => 1 (with mask 00000100, shift 2)
    # in the end, 10110101 becomes [1,0,1,1,0,1,0,1]

def _hide(text:bytes, picture_data):
    """generator hiding the text in picture_data (PIL.Image.Image.getdata).
    yields : int"""
    picture_data = itertools.chain.from_iterable(picture_data)
    ret = [t|(p&254) for t,p in zip(_titer(text), picture_data)]
    # we now have to assert picture_data ends on a pixel
    while len(ret)%BANDS :
        ret.append(next(picture_data))
    return ret

def _show(picture_data):
    """Generator yielding the text hidden in the picture_data.
    yield : int"""
    a = (p&1 for p in itertools.chain.from_iterable(picture_data))
    b = ((p<<c, c) for p,c in zip(a, itertools.cycle(range(7,-1,-1))))
    z = 0
    for x,c in b :
        z |= x
        if not c :
            yield z
            z = 0

def _bundle(data) :
    """Bundles <data> (iterable) by groups of BANDS elements,
    for use by PIL.Image.Image.putdata. (undoes itertools.chain)"""
    def f(x,y):
        y = (y,)
        if len(x) == BANDS :
            return y
        else :
            return x + y

    return tuple(x for x in
        itertools.accumulate(itertools.chain( ((),), data), f)
            if len(x)==BANDS)

def hide(text:bytes, image:PIL.Image.Image)->None :
    """Hides the text in the image. Returns nothing, but modifies the image"""
    l = len(text).to_bytes(FLAG_SIZE, "big")
    text = l+text
    if len(text)*8 > operator.mul(*image.size)*3 :
        print("WARNING : can't hide so much data in this picture ! The data will be truncated")
    image.putdata(_bundle(_hide(text, image.getdata())))

def show(image:PIL.Image.Image) :
    """Generator revealing the message hidden in the image.
    yield : int"""
    it = _show(image.getdata())
    l = int.from_bytes(bytes(itertools.islice(it, FLAG_SIZE)), "big")
    return bytes(itertools.islice(it, l))
