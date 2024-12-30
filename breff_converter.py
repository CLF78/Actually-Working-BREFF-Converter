#!/usr/bin/env python3

# breff_converter.py
# Converts a BREFF file to a series of JSON files and back

import sys
from pathlib import Path
from common.args import args
from common.common import META_FILE, json_dump, json_load, printv
from common.nw4r import NameString
from effect.effect import BinaryFileHeader, EffectTable, EffectTableEntry, Effect

if sys.version_info < (3, 11):
    raise SystemExit('Please update your copy of Python to 3.11 or greater. Currently running on: ' + sys.version.split()[0])

def decode(src: Path, dst: Path) -> None:

    # Ensure file format matches
    # TODO remove this and check the magic instead
    if src.suffix != '.breff':
        raise SystemExit(f'Unknown file format with binary extension {src.suffix}.')

    # Ensure file exists
    if not src.is_file():
        raise SystemExit(f'Could not find file {src}.')

    # Ensure the destination does not exist if overwrite is not specified
    if dst.is_dir() and not args.overwrite:
        raise SystemExit(f'Destination directory {dst} already exists.')

    # Create the destination directory
    dst.mkdir(parents=True, exist_ok=True)

    # Open file and decode it
    printv(f'Parsing file {src}...')
    src_data = src.read_bytes()
    header, _ = BinaryFileHeader.from_bytes(src_data)

    # Write the meta file
    meta_file = Path(dst, META_FILE)
    json_dump(meta_file, header.to_json())

    # Create the effect table from the project data, then iterate it
    effect_table, _ = EffectTable.from_bytes(header.block.project.project_data)
    for entry in effect_table.entries:

        printv(f'Parsing effect {entry.name.name}...')
        effect, _ = Effect.from_bytes(entry.data)
        effect_file = Path(dst, f'{entry.name.name}.json')
        json_dump(effect_file, effect.to_json())


def encode(src: Path, dst: Path) -> None:

    # Ensure directory exists
    if not src.is_dir():
        raise SystemExit(f'Could not find directory {src}.')

    # Ensure a meta file is present in the directory
    meta_file = Path(src, META_FILE)
    if not meta_file.is_file():
        raise SystemExit(f'Missing metadata file in directory {src}.')

    # Ensure the destination does not exist if overwrite is not specified
    if dst.is_file() and not args.overwrite:
        raise SystemExit(f'Destination file {dst} already exists.')

    # Read the meta file
    printv(f'Parsing directory {src}...')
    meta_data = json_load(meta_file)
    header = BinaryFileHeader.from_json(meta_data)

    # Create the effect table
    effect_table = EffectTable()

    # Parse each effect file (ensure the files are sorted)
    for file in sorted(src.glob('*.json')):

        # Skip the meta file
        if file == meta_file:
            continue

        # Create the effect and encode it
        printv(f'Parsing {file}...')
        effect_data = json_load(file)
        effect = Effect.from_json(effect_data).to_bytes()

        # Create the table entry
        effect_table_entry = EffectTableEntry(effect_table)
        effect_table_entry.data = effect
        effect_table_entry.name = NameString(effect_table_entry)
        effect_table_entry.name.name = file.stem
        effect_table.entries.append(effect_table_entry)

    # Encode the effect table and insert it into the project
    header.block.project.project_data = effect_table.to_bytes()

    # Write the file out
    dst.write_bytes(header.to_bytes())


if __name__ == '__main__':

    # Define valid operations
    operations = {
        'decode': decode,
        'encode': encode,
    }

    # Get inputs and outputs
    args.sources = args.sources[0]
    if args.dests is None:
        if args.operation == 'decode':
            args.dests = [file.with_suffix('.breff.d') for file in args.sources]
        else:
            args.dests = [file.with_suffix('').with_suffix('.breff') for file in args.sources]

    # Ensure the amount of destinations equals the number of sources
    if len(args.dests) != len(args.sources):
        raise SystemExit('Wrong number of output paths.')

    # Execute function
    for src, dest in zip(args.sources, args.dests):
        operations[args.operation](src, dest)
