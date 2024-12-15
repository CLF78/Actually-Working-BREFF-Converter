#!/usr/bin/env python3

# common.py
# Common utilities

from enum import IntEnum

META_FILE = 'meta.json5'

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
    return components[0] + ''.join(x.title() for x in components[1:])


# Utility function to convert camelCase to snake_case
def camel_to_snake(camel_str: str) -> str:
    return ''.join(['_' + c.lower() if c.isupper() else c for c in camel_str]).lstrip('_')


# Utility function to convert PascalCase to camelCase
def pascal_to_camel(pascal_str: str) -> str:
    return pascal_str[0].lower() + pascal_str[1:]


# Utility function to convert camelCase to PascalCase
def camel_to_pascal(camel_str: str) -> str:
    return camel_str[0].upper() + camel_str[1:]


# Utility function to convert snake_case to PascalCase
def snake_to_pascal(snake_str: str) -> str:
    return ''.join(x.title() for x in snake_str.split('_'))


# Utility function to convert PascalCase to snake_case
def pascal_to_snake(pascal_str: str) -> str:
    return ''.join(['_' + c.lower() if c.isupper() else c for c in pascal_str]).lstrip('_')


# An enum whose value starts from zero
class CEnum(IntEnum):
    @classmethod
    def _generate_next_value_(cls, name, start, count, last_values):
        return last_values[-1] + 1 if last_values else 0
