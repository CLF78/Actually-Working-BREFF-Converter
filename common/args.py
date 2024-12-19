#!/usr/bin/env python3

# args.py
# Args management

import argparse
from pathlib import Path

def get_args():
    parser = argparse.ArgumentParser(description='Converts a BREFF file to a set of JSON files and back')
    parser.add_argument('operation', choices=['decode', 'encode'], help='The operation to execute')
    parser.add_argument('inputs', nargs='+', type=Path, help='The files/directories to convert', action='append')
    parser.add_argument('-o', '--outputs', nargs='*', type=Path, help='The output directory/file for each input')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    return parser.parse_args()

args = get_args()
