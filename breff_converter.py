#!/usr/bin/env python3

# breff_converter.py
# Converts a BREFF file to JSON5 and back

import argparse
import json5
from pathlib import Path
from effect.header import BinaryFileHeader


def decode(src: Path, dst: Path) -> None:

    # Ensure file format matches
    if src.suffix != '.breff':
        raise SystemExit(f'Unknown file format with binary extension {src.suffix}.')

    # Ensure file exists
    if not src.is_file():
        raise SystemExit(f'Could not find file {src}.')

    # Open file and decode it
    src_data = src.read_bytes()
    dst_data = BinaryFileHeader.from_bytes(src_data).to_json()

    # Write the result
    with open(dst, 'w', encoding='utf-8') as f:
        json5.dump(dst_data, f, indent=4)


def encode(src: Path, dst: Path) -> None:
    return


if __name__ == '__main__':

    # Define valid operations
    operations = {
        'decode': decode,
        'encode': encode,
    }

    # Parse command line args
    parser = argparse.ArgumentParser(description='Converts a BREFF file to JSON5 and back')
    parser.add_argument('operation', choices=operations.keys(), help='The operation to execute')
    parser.add_argument('inputs', nargs='+', type=Path, help='The files to convert', action='append')
    parser.add_argument('-o', '--outputs', nargs='*', type=Path, help='The converted file outputs')
    args = parser.parse_args()

    # Get inputs and outputs
    args.inputs = args.inputs[0]
    if args.outputs is None:
        if args.operation == 'decode':
            args.outputs = [file.with_name(file.name + '.json5') for file in args.inputs]
        else:
            args.outputs = [file.with_suffix('') for file in args.inputs]
    else:
        args.outputs = args.outputs[0]

    # Ensure the amount of outputs equals the number of inputs
    if len(args.outputs) != len(args.inputs):
        raise SystemExit('Wrong number of output paths.')

    # Execute function
    for src, dest in zip(args.inputs, args.outputs):
        operations[args.operation](src, dest)
