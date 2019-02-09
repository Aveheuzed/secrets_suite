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

# input / de-steganographying
if args.show :
    print("showing...", end="", flush=True)
    current_data = stegano.show(Image.open(args.source).convert("RGB"))
elif args.source is None :
    print("Type your input (double return when done) : ")
    source = list()
    i = input()
    while i :
        source.append(i.encode())
        i = input()
    del i
    source = b"\n".join(source)
    current_data = source
else :
    current_data = open(args.source,"rb").read()

# deciphering
if args.decipher :
    print("deciphering...", end="", flush=True)
    current_data = cipher.decipher(current_data, pwdd)

# ciphering
if args.cipher :
    print("ciphering...", end="", flush=True)
    current_data = cipher.cipher(current_data, pwdc)

# output / steganographying
if args.hide :
    print("hiding...", end="", flush=True)
    support = Image.open(args.hide)
    if support.mode == "RGBA" :
        alpha = support.split()[-1]
    support = support.convert("RGB")

    stegano.hide(current_data, support)

    if "alpha" in locals().keys() :
        support.putalpha(alpha)
    support.save(args.output)
    print("done.")
elif args.output is None :
    print("done.\n")
    print(current_data.decode(errors="replace"))
else :
    print("done.")
    if not args.output.parent.exists() : # making the necessary subfolders, if needed
        args.output.parent.mkdir(parents=True)
    with open(args.output, "wb") as file :
        file.write(current_data)
