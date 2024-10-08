#!/usr/bin/env python3

# common.py
# Common utilities

import struct
from dataclasses import dataclass, field, fields, Field, MISSING
from typing import Optional, TypeVar, Type, get_origin
from enum import Flag, Enum

T = TypeVar('T', bound='BaseBinary')
IGNORE_JSON = {'ignore_json': True}       # Ignores the field when exporting to/reading from JSON
IGNORE_BINARY = {'ignore_binary': True}   # Ignores the field when exporting to/reading from binary
STRUCT = lambda s: {'struct_format': struct.Struct(f'>{s}')} # Defines the structure for the field (only for basic data types)
OVERRIDE_NAME = lambda s: {'override': s} # Overrides a field name in the exported JSON format
UNROLL_CONTENT = {'unroll_content': True} # Merges the field contents instead of putting them under a key (dataclass only)
ALIGN_PAD = lambda s: {'align_pad': s}    # Aligns the field by s bytes

# Aligns an integer to the given value
def align(value: int, alignment: int) -> int:
    return value + alignment - value % alignment

# Pads a byte array to the given alignment
def pad(data: bytes, alignment: int):
    aligned_size = align(len(data), alignment)
    return data if not aligned_size else data + b'\0' * aligned_size

# Convert snake_case to camelCase
def snake_to_camel(snake_str: str) -> str:
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

# Utility function to convert camelCase to snake_case
def camel_to_snake(camel_str: str) -> str:
    return ''.join(['_' + c.lower() if c.isupper() else c for c in camel_str]).lstrip('_')


@dataclass
class BaseBinary:
    parent: Optional[T] = field(default=None, metadata=IGNORE_JSON | IGNORE_BINARY)

    @classmethod
    def from_bytes(cls: Type[T], data: bytes, offset: int = 0, parent: Optional[T] = None) -> T:
        """
        Create an instance of cls from a byte sequence.
        """

        # Create the class and set the parent
        obj = cls()
        obj.parent = parent

        # Iterate the class fields
        for field in fields(cls):

            # Get the field data
            field_name = field.name
            field_type = field.type
            field_meta = field.metadata

            # If the field is marked as ignored, skip it
            if field_meta.get('ignore_binary', False):
                continue

            # Get the struct format, if it has one unpack it and set the field
            # Also works for enums
            struct_format: struct.Struct = field_meta.get('struct_format')
            if struct_format:
                field_size = struct_format.size
                field_value = field_type(struct_format.unpack_from(data, offset)[0])
                setattr(obj, field_name, field_value)
                offset += field_size

            # If it's a dataclass, recursively deserialize it
            elif issubclass(field_type, BaseBinary):
                field_value = field_type.from_bytes(data, offset, obj)
                setattr(obj, field_name, field_value)
                offset += field_value.size()

            # If it's a string, do not rely on any given length values but find the ending NULL character
            elif field_type == str:
                value_end = data.index(b'\0', offset)
                field_value = data[offset:value_end].decode('ascii')
                setattr(obj, field_name, field_value)
                offset = value_end + 1

            # If the field is padded, skip the necessary bytes
            if field_meta.get('align_pad', 0):
                offset = align(offset, field_meta['align_pad'])

            # Validate the field
            obj.validate(len(data), field)

        # Return the finished object
        return obj

    def to_bytes(self) -> bytes:
        """
        Serialize the instance to a byte sequence.
        """

        # Initialize result
        result = b''

        # Iterate the class fields
        for field in fields(self):

            # Get field data
            field_name = field.name
            field_meta = field.metadata
            field_value = getattr(self, field_name)

            # Ignore the field if it should not be exported
            if field_meta.get('ignore_binary', False):
                continue

            # If it has a format, use it for packing
            struct_format: struct.Struct = field_meta.get('struct_format')
            if struct_format:
                result += struct_format.pack(field_value)

            # If it's a dataclass, recursively serialize it
            elif isinstance(field_value, BaseBinary):
                result += field_value.to_bytes()

            # If it's a string, encode it and null terminate it
            elif isinstance(field_value, str):
                result += field_value.encode('ascii') + b'\0'

            # If the field is padded, do so
            if field_meta.get('align_pad', 0):
                result = pad(result, field_meta['align_pad'])

        # Return final result
        return result

    @classmethod
    def from_json(cls: Type[T], data: dict, parent: Optional[T] = None) -> T:
        """
        Create an instance from a JSON-like dictionary.
        """

        # Create the class and set the parent
        obj = cls()
        obj.parent = parent

        # Parse each field
        for field in fields(cls):
            field_name = field.name
            field_type = field.type
            field_default = field.default
            field_default_factory = field.default_factory
            field_meta = field.metadata

            # Skip the field if it should be ignored
            if field_meta.get('ignore_json', False):
                continue

            # If the field is to be read with a different name, do so
            if field_meta.get('override'):
                field_json_name = field_meta['override']
            else:
                field_json_name = snake_to_camel(field_name)

            # Check if the data is there
            if field_json_name in data or field_meta.get('unroll_content', False):

                # If it's a dataclass, construct it recursively
                if issubclass(field_type, BaseBinary):

                    # Use the same dict if unrolled
                    if field_meta.get('unroll_content', False):
                        setattr(obj, field_name, field_type.from_json(data, obj))
                    else:
                        setattr(obj, field_name, field_type.from_json(data[field_json_name], obj))

                # For lists, ensure it's a list and parse it
                elif get_origin(field_type) == list:
                    if not isinstance(data[field_json_name], list):
                        raise TypeError(f'Expected a list for field {field_name}')

                    # Check if the underlying type is a dataclass or not
                    list_type = field_type.__args__[0]
                    if issubclass(list_type, BaseBinary):
                        setattr(obj, field_name, [field_type.__args__[0].from_json(value, obj) for value in data[field_json_name]])
                    else:
                        setattr(obj, field_name, [value for value in data[field_json_name]])

                # For Flags, look for each flag separately
                elif issubclass(field_type, Flag):

                    # Ensure flags is a dictionary
                    flags = data[field_json_name]
                    if not isinstance(flags, dict):
                        raise TypeError(f'Expected a dict for field {field_name}')

                    # Build the enum flag
                    value = field_type(0)
                    for flag in field_type:
                        if flags.get(flag.name, False):
                            value |= flag

                    # Set value
                    setattr(obj, field_name, value)

                # For enums, convert from string
                elif issubclass(field_type, Enum):

                    # Ensure value is a string
                    value = data[field_json_name]
                    if not isinstance(value, str):
                        raise TypeError(f'Expected a string for field {field_name}')

                    # Set it
                    setattr(obj, field_name, field_type[value])

                # Else verify the type matches the expected one, and if so set it
                else:
                    value = data[field_json_name]
                    if not isinstance(value, field_type):
                        raise TypeError(f'Expected type {field_type} for field {field_name}')

                    # If valid, set it
                    setattr(obj, field_name, value)

            # If not found, try using the default value
            elif field_default is not MISSING:
                setattr(obj, field_name, field_default)

            # Try also the default factory
            elif field_default_factory is not MISSING:
                setattr(obj, field_name, field_default_factory())

            # Else just bail
            else:
                raise ValueError(f'Missing value for field {field_name}')

        # Return built object
        return obj

    def to_json(self) -> dict:
        """
        Serialize the instance to a JSON-like dictionary.
        """

        # Initialize the result
        result = {}

        # Parse each field
        for field in fields(self):

            # Get info
            field_name = field.name
            field_meta = field.metadata
            field_type = field.type

            # If the field must not be exported, skip it
            if field_meta.get('ignore_json', False):
                continue

            # If the field is to be read with a different name, do so
            if field_meta.get('override'):
                field_json_name = field_meta['override']
            else:
                field_json_name = snake_to_camel(field_name)

            # Get the value
            field_value = getattr(self, field_name)

            # If it's a dataclass, convert it to dictionary using its method
            if isinstance(field_value, BaseBinary):
                value = field_value.to_json()

                # If it needs to be unrolled, simply merge the result into the given dictionary
                if field_meta.get('unroll_content', False):
                    result |= value

                # Else just store it under the key
                else:
                    result[field_json_name] = field_value.to_json()

            # If it's a list, convert each value and store the resulting list
            elif isinstance(field_value, list):

                # If the type is a dataclass, use its method for storing
                if (issubclass(field_type.__args__[0], BaseBinary)):
                    result[field_json_name] = [value.to_json() for value in field_value]
                else:
                    result[field_json_name] = [value for value in field_value]

            # For Flags, store each flag separately
            elif isinstance(field_value, Flag):
                result[field_json_name] = {flag.name: bool(flag in field_value) for flag in field_type}

            # For Enums, convert to string
            elif isinstance(field_value, Enum):
                result[field_json_name] = field_value.name

            # Otherwise just store the value as is
            else:
                result[field_json_name] = field_value

        # Return resulting dict
        return result

    def size(self) -> int:
        """
        Get the size of the structure in bytes
        """

        # Initialize loop
        size = 0
        for field in fields(self):

            # Get field data
            field_name = field.name
            field_meta = field.metadata

            # Ignore fields with the ignore binary flag and kw_only fields
            if field_meta.get('ignore_binary', False) or field.kw_only:
                continue

            # If the field has an associated structure, use it to calculate the size
            struct_format: struct.Struct = field_meta.get('struct_format')
            if struct_format:
                size += struct_format.size

            # Else use the value for the calculation
            else:
                field_value = getattr(self, field_name)

                # For dataclasses, use the size method recursively
                if isinstance(field_value, BaseBinary):
                    size += field_value.size()

                # For strings, calculate the length
                elif isinstance(field_value, str):
                    size += len(field_value) + 1

        # Return result
        return size

    def validate(self, data_length: int, field: Field) -> None:
        return


@dataclass
class VEC3(BaseBinary):
    x: float = field(default=0.0, metadata=STRUCT('f'))
    y: float = field(default=0.0, metadata=STRUCT('f'))
    z: float = field(default=0.0, metadata=STRUCT('f'))
