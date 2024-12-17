#!/usr/bin/env python3

# breff_decode.py
# Converts a BREFF file to a series of JSON5 files

import argparse
from pathlib import Path
from common.common import META_FILE, json_dump
from effect.effect import BinaryFileHeader, EffectTable, Effect

def decode(src: Path, dst: Path) -> None:

    # Ensure file format matches
    if src.suffix != '.breff':
        raise SystemExit(f'Unknown file format with binary extension {src.suffix}.')

    # Ensure file exists
    if not src.is_file():
        raise SystemExit(f'Could not find file {src}.')

    # Ensure the destination directory exists
    dst.mkdir(parents=True, exist_ok=True)

    # Open file and decode it
    src_data = src.read_bytes()
    header, _ = BinaryFileHeader.from_bytes(src_data)

    # Write the meta file
    meta_file = Path(dst, META_FILE)
    json_dump(meta_file, header.to_json())

    # Create the effect table from the project data, then iterate it
    effect_table, _ = EffectTable.from_bytes(header.block.project.project_data)
    for entry in effect_table.entries:

        #print(f'Parsing {entry.name.name}...')
        effect, _ = Effect.from_bytes(entry.data)
        effect_file = Path(dst, f'{entry.name.name}.json')
        json_dump(effect_file, effect.to_json())


if __name__ == '__main__':

    # Parse command line args
    parser = argparse.ArgumentParser(description='Converts a BREFF file to a set of JSON files')
    parser.add_argument('inputs', nargs='+', type=Path, help='The files to convert', action='append')
    parser.add_argument('-o', '--outputs', nargs='*', type=Path, help='The output directory for each file')
    args = parser.parse_args()

    # Get inputs and outputs
    args.inputs = args.inputs[0]
    if args.outputs is None:
        args.outputs = [file.with_suffix('.d') for file in args.inputs]
    else:
        args.outputs = args.outputs[0]

    # Ensure the amount of outputs equals the number of inputs
    if len(args.outputs) != len(args.inputs):
        raise SystemExit('Wrong number of output paths.')

    # Execute function
    for src, dest in zip(args.inputs, args.outputs):
        decode(src, dest)
