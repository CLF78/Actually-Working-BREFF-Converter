#!/usr/bin/env python3

# common.py
# Common utilities

import re
from enum import IntEnum
from pathlib import Path
from common.args import args

META_FILE = 'meta.json'

try:
    import orjson

    def json_dump(path: Path, data: dict) -> None:
        path.write_bytes(orjson.dumps(data, option=orjson.OPT_INDENT_2))

    def json_load(path: Path) -> dict:
        return orjson.loads(path.read_bytes())

except ImportError:
    import json

    def json_dump(path: Path, data: dict) -> None:
        data = json.dumps(data, separators=(',', ': '), indent=2)
        path.write_text(data, encoding='utf-8')

    def json_load(path: Path) -> dict:
        data = path.read_text(encoding='utf-8')
        return json.loads(data)


# Debug print helper
def printv(*arguments, **kwargs):
    global args
    if args.verbose:
        print(*arguments, **kwargs)


# Aligns an integer to the given value
def align(value: int, alignment: int) -> int:
    return (value + alignment - 1) & ~(alignment - 1)


# Pads a byte array to the given alignment
def pad(data: bytes, alignment: int):
    length = len(data)
    aligned_size = align(length, alignment)
    return data + b'\0' * (aligned_size - length)


# Convert snake_case to camelCase
def snake_to_camel(snake_str: str) -> str:
    components = snake_str.split('_')
    return components[0] + ''.join(x.capitalize() for x in components[1:])


# Utility function to convert camelCase to snake_case
CAMEL_TO_SNAKE_PATTERN = re.compile(r'([a-z0-9])([A-Z])')
def camel_to_snake(camel_str: str) -> str:
    return CAMEL_TO_SNAKE_PATTERN.sub(r'\1_\2', camel_str).lower()


# Utility function to convert PascalCase to camelCase
def pascal_to_camel(pascal_str: str) -> str:
    return pascal_str[0].lower() + pascal_str[1:]


# Utility function to convert camelCase to PascalCase
def camel_to_pascal(camel_str: str) -> str:
    return camel_str[0].upper() + camel_str[1:]


# Utility function to convert snake_case to PascalCase
def snake_to_pascal(snake_str: str) -> str:
    return ''.join(x.capitalize() for x in snake_str.split('_'))


# Utility function to convert PascalCase to snake_case
PASCAL_TO_SNAKE_PATTERN = re.compile(r'([A-Z])')
def pascal_to_snake(pascal_str: str) -> str:
    return PASCAL_TO_SNAKE_PATTERN.sub(r'_\1', pascal_str).lower().lstrip('_')


# An enum whose value starts from zero
class CEnum(IntEnum):
    @classmethod
    def _generate_next_value_(cls, name, start, count, last_values):
        return last_values[-1] + 1 if last_values else 0
