#!/usr/bin/env python3
import itertools
import PIL.Image

"""Steganography utilities. Hides (or reveals) the message hidden
in the lsb of each pixel of the picture (on each channel)
The length of the message is hidden before it, on FLAG_SIZE bytes
(ending on 8*FLAG_SIZE bytes of picture data)"""

FLAG_SIZE = 4
# size (in bytes) of the start flag, indicating the text's length

def _titer(text:bytes):
    """Generator splitting bytes into bits, using logical operators.
    yield : int (0 or 1)"""
    masks = [(1<<x, x) for x in range(7,-1,-1)]
    for t in text :
        for m, s in masks :
            yield (t&m)>>s
    # 10110101 => 00000100 => 1 (with mask 00000100, shift 2)

def _hide(text:bytes, picture_data):
    """generator hiding the text in picture_data (PIL.Image.Image.getdata).
    yields : int"""
    if not isinstance(picture_data[0], int) : # we need a flat iterable of int
        picture_data = itertools.chain.from_iterable(picture_data)
    else :
        picture_data = iter(picture_data)
    ret = [p|(t&254) for p,t in zip(_titer(text), picture_data)]
    # we now have to assert picture_data ends on a pixel
    while len(ret)%3 : # WARNING: magic number here : 3 (R, V, B)
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

def _bundle(data, bands:int=3) :
    """Bundles <data> (iterable) by groups of <band> elements,
    for use by PIL.Image.Image.putdata. (undoes itertools.chain)
    Does nothing (returns <data>) if <band> <= 1"""
    if bands <= 1 : # nothing to do
        return tuple(data)
    def f(x,y):
        x = x + (y,)
        if len(x) >= bands :
            return tuple()
        else :
            return x

    return tuple(x for x in
        itertools.accumulate(itertools.chain( ((),), data), f)
            if len(x)==bands)

def hide(text:bytes, image:PIL.Image.Image)->None :
    """Hides the text in the image. Returns nothing, but modifies the image"""
    l = len(text).to_bytes(FLAG_SIZE, "big")
    text = l+text
    image.putdata(_bundle(_hide(text, image.getdata())))

def show(image:PIL.Image.Image) :
    """Generator revealing the message hidden in the image.
    yield : int"""
    it = _show(image.getdata())
    l = int.from_bytes(bytes(itertools.islice(it, FLAG_SIZE)), "big")
    return bytes(itertools.islice(it, l))
