#!/usr/bin/env python3

"""This script can be used to cipher, decipher,
hide a message in a picture or reveal the hidden message from a picture (steganography)"""

import argparse, getpass, io, sys
from PIL import Image
import stegano
import cipher
import pathlib

def _checkpath(path:str)->pathlib.Path:
    """filter to ensure the path exists ; otherwise, raises an ArgumentTypeError"""
    path = pathlib.Path(path)
    if path.exists() :
        return path
    else :
        raise argparse.ArgumentTypeError("This path does not exist")

def _genonfh(fh:open):
    """generator yielding the content of the file handler (readable) one character at a time,
    to be able to iterate on the file handler as if it were on its content (saves time and memory)
    yields : int"""
    data = True
    while data : # when exhausted, the read() method return an empty str|bytes
        data = fh.read(1)
        if data :
            yield ord(data)


parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, epilog="""
The specified actions are taken in the following order :
1) show
2) decipher
3) cipher
4) hide
""")

# arguments are split in groups, in order to improve readability
protect = parser.add_argument_group("protect")
reveal = parser.add_argument_group("reveal")
i_o = parser.add_argument_group("I/O", "You may ommit these arguments in order to use stdin or stdout")

protect.add_argument("--hide", "-H", default=False, help="hides the input into the given picture", type=_checkpath)
protect.add_argument("--cipher", "-c", action="store_true", help="ciphers the input")
reveal.add_argument("--show", "-s", action="store_true", help="reveals the message hidden in the input picture")
reveal.add_argument("--decipher", "-d", action="store_true", help="deciphers the input")

i_o.add_argument("--from", "-f", required=False, help="file to read data from", type=_checkpath, dest="source")
i_o.add_argument("--to", "-t", required=False, help="file to write the result to", type=pathlib.Path, dest="output")


args = parser.parse_args() # parses arguments from the command line


if args.cipher :
    pwdc = getpass.getpass("cipher password : ").encode()
if args.decipher :
    pwdd = getpass.getpass("decipher password : ").encode()

processes = list() # this list contains the processing generators, piped to each other

# input / de-steganographying
if args.show :
    print("showing...", end="")
    processes.append(stegano.show(Image.open(args.source)))
elif args.source is None :
    print("Type your input (double return when done) : ")
    source = list()
    i = input()
    while i :
        source.append(i.encode())
        i = input()
    del i
    source = b"\n".join(source)
    processes.append(source)
else :
    source = open(args.source,"rb")
    processes.append(_genonfh(source))

# deciphering
if args.decipher :
    print("deciphering...", end="")
    processes.append(cipher.decipher(processes[-1], pwdd))

# ciphering
if args.cipher :
    print("ciphering...", end="")
    processes.append(cipher.cipher(processes[-1], pwdc))

# output / steganographying
if args.hide :
    print("hiding...", end="")
    support = Image.open(args.hide)
    processes.append(stegano.hide(bytes(processes[-1]), support))
    support.save(args.output)
    print("done.")
elif args.output is None :
    print("done.\n")
    print(bytes(processes[-1]).decode(errors="replace"))
else :
    print("done.")
    if not args.output.parent.exists() : # making the necessary subfolders, if needed
        args.output.parent.mkdir(parents=True)
    with open(args.output, "wb") as file :
        for u in processes[-1] :
            file.write(u.to_bytes(1,"big"))
