#!/usr/bin/env python

# Copyright (c) 2019 Fabien LOISON <https://www.flozz.fr/>
#
#        DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#                    Version 2, December 2004
#
# Copyright (C) 2004 Sam Hocevar <sam@hocevar.net>
#
# Everyone is permitted to copy and distribute verbatim or modified
# copies of this license document, and changing it is allowed as long
# as the name is changed.
#
#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
#
#  0. You just DO WHAT THE FUCK YOU WANT TO.


import re
import sys
import os.path
import argparse


VERSION = "1.0.0"

_asxxxx_regexp = re.compile(r"^\s+([0-9A-F]{8})\s+([^ ]+)")
_old_gbdk_regexp = re.compile(r"^\t\t([^\t]+)\t([0-9A-F]{4})$")


def read_old_gbdk_map(map_):
    for line in map_.split("\n"):
        match = _old_gbdk_regexp.match(line)
        if not match:
            continue
        addr = int(match.group(2), 16)
        bank = addr // 0x4000 if addr <= 0x07FFF else 0
        name = match.group(1)
        yield bank, addr, name


def read_asxxxx_map(map_):
    for line in map_.split("\n"):
        match = _asxxxx_regexp.match(line)
        if not match:
            continue
        addr = int(match.group(1), 16)
        bank = addr // 0x4000 if addr <= 0x07FFF else 0
        name = match.group(2)
        yield bank, addr, name


def is_asxxxx_map(map_):
    return map_.startswith("\x0cASxxxx Linker")


def generate_nogmb_sym(symboles):
    sym = ""
    for bank, addr, name in symboles:
        sym += "%02X:%04X %s\n" % (bank, addr, name)
    return sym


def maptosym(input_map_file, output_sym_file):
    map_ = input_map_file.read()
    if is_asxxxx_map(map_):
        symboles = read_asxxxx_map(map_)
    else:
        symboles = read_old_gbdk_map(map_)
    nogmb_sym = generate_nogmb_sym(symboles)
    output_sym_file.write(nogmb_sym)


def gen_output_filename(input_filename):
    base, ext = os.path.splitext(input_filename)
    return "%s.sym" % base


def make_cli():
    parser = argparse.ArgumentParser(
            description="TODO"
            )

    parser.add_argument(
            "-v",
            "--version",
            action="version",
            version=VERSION
            )

    parser.add_argument(
            "map_file",
            type=argparse.FileType("r"),
            help="The input .map file"
            )

    return parser


def main(argv=sys.argv):
    parser = make_cli()
    args = parser.parse_args(argv[1:])
    output_sym_filename = gen_output_filename(args.map_file.name)
    output_sym_file = open(output_sym_filename, "w")
    maptosym(args.map_file, output_sym_file)


if __name__ == "__main__":
    main()
