#!/usr/bin/env python3

# common.py
# Common utilities

import struct
from dataclasses import dataclass, field, fields, Field, MISSING
from typing import Optional, Union, TypeVar, Type, get_origin, final
from enum import Flag, Enum

T = TypeVar('T', bound='BaseBinary')
META_FILE = 'meta.json5'

ALIGN_PAD = 'align_pad'
COUNT_FIELD = 'count_field'
IGNORE_JSON = 'ignore_json'
IGNORE_BINARY = 'ignore_binary'
STRUCT = 'struct'
UNROLL_CONTENT = 'unroll_content'

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


# Generates an extended field with the given settings
# TODO remove
def fieldex(structure: str = None, ignore_binary: bool = False, ignore_json: bool = False,
            unroll_content: bool = False, align_pad: int = 1, count_field: str = None,
            default=MISSING, default_factory=MISSING, **kwargs) -> Field:

    # Replace any given metadata
    kwargs['metadata'] = {
        STRUCT: struct.Struct(f'>{structure}') if structure else None,
        IGNORE_BINARY: ignore_binary,
        IGNORE_JSON: ignore_json,
        UNROLL_CONTENT: unroll_content,
        ALIGN_PAD: max(1, align_pad),
        COUNT_FIELD: count_field
    }

    # Replace kw_only and init arguments
    kwargs['kw_only'] = True
    kwargs['init'] = False

    # Use default or default factory if provided
    if default is not MISSING:
        kwargs['default'] = default
    elif default_factory is not MISSING:
        kwargs['default_factory'] = default_factory

    # Return the created field
    return field(**kwargs)


# An enum whose value starts from zero
class CEnum(Enum):
    @classmethod
    def _generate_next_value_(cls, name, start, count, last_values):
        return last_values[-1] + 1 if last_values else 0


# Base class for all structures to allow recursive data packing/unpacking
# TODO remove
@dataclass
class BaseBinary:
    parent: Optional[T] = fieldex(ignore_binary=True, ignore_json=True, default=None)

    @final
    def __post_init__(self):
        """
        Automatically initializes all fields that do not have a default.
        """
        for field in fields(self):

            # Skip fields with defaults
            if field.default is not MISSING or field.default_factory is not MISSING:
                continue

            field_type = field.type
            field_name = field.name

            if field_type is int:
                setattr(self, field_name, 0)
            elif field_type is bool:
                setattr(self, field_name, False)
            elif field_type is float:
                setattr(self, field_name, 0.0)
            elif field_type is bytes:
                setattr(self, field_name, b'')
            elif field_type is str:
                setattr(self, field_name, '')
            elif get_origin(field_type) == list:
                setattr(self, field_name, [])
            elif isinstance(field_type, type) and issubclass(field_type, Enum):
                setattr(self, field_name, 0)
            elif isinstance(field_type, type) and issubclass(field_type, BaseBinary):
                setattr(self, field_name, field_type())
            else:
                raise ValueError(f'Missing default value for field {type(self)}.{field.name} ({field_type})')

    @final
    def field_from_bytes(self, field: Union[Field, str], data: bytes, offset: int = 0) -> int:
        """
        Decodes a field from a binary sequence using the field's metadata.
        Returns the updated offset after parsing the field.
        """

        # Get the field if a string is passed
        if type(field) == str:
            field = self.__dataclass_fields__[field]

        # Get the field data
        field_name = field.name
        field_type = field.type
        field_meta = field.metadata

        # Get the struct format
        struct_format: struct.Struct = field_meta[STRUCT]

        # If it's a list, get the count field and unpack each entry
        if get_origin(field_type) == list:
            if not field_meta[COUNT_FIELD]:
                raise ValueError('Missing count field for list field', field_name)

            # Get the list type and list
            list_type = field_type.__args__[0]
            container: list = getattr(self, field_name)

            # Get the counter value
            count = self
            for attr in field_meta[COUNT_FIELD].split('.'):
                count = getattr(count, attr)

            # If the field is a dataclass, iteratively deserialize it
            if isinstance(list_type, type) and issubclass(list_type, BaseBinary):
                for _ in range(count):
                    entry = list_type.from_bytes(data, offset, self)
                    container.append(entry)
                    offset += entry.size()

            # Else if a struct is provided, use it for unpacking
            elif struct_format:
                for _ in range(count):
                    container.append(struct_format.unpack_from(data, offset)[0])
                    offset += struct_format.size

            # Else bail
            else:
                raise ValueError('Missing structure definition for list field', field_name)

        # If a struct is provided, use it to unpack and set the field
        # Also works for enums
        elif struct_format:
            field_size = struct_format.size
            field_value = field_type(struct_format.unpack_from(data, offset)[0])
            setattr(self, field_name, field_value)
            offset += field_size

        # If it's a dataclass, recursively deserialize it
        elif issubclass(field_type, BaseBinary):
            field_value = field_type.from_bytes(data, offset, self)
            setattr(self, field_name, field_value)
            offset += field_value.size()

        # If it's a string, do not rely on any given length values but find the ending NULL character
        elif field_type == str:
            value_end = data.index(b'\0', offset)
            field_value = data[offset:value_end].decode('ascii')
            setattr(self, field_name, field_value)
            offset = value_end + 1

        # Skip alignment bytes
        offset = align(offset, field_meta[ALIGN_PAD])

        # Return updated offset
        return offset

    @final
    def field_to_bytes(self, field: Union[Field, str]) -> bytes:
        """
        Serializes a field to a binary sequence. Returns the encoded field.
        """

        # Get the field if a string is passed
        if type(field) == str:
            field = self.__dataclass_fields__[field]

        # Get field data
        field_name = field.name
        field_meta = field.metadata
        field_value = getattr(self, field_name)

        # Initialize result
        result = b''

        # Get struct format
        struct_format: struct.Struct = field_meta[STRUCT]

        # If it a list, pack it iteratively
        if isinstance(field_value, list):

            # Get the list's contained type
            list_type = field.type.__args__[0]

            # If the contained data is a dataclass, iteratively deserialize it
            if isinstance(list_type, type) and issubclass(list_type, BaseBinary):
                for item in field_value:
                    result += item.to_bytes()

            # Else if a struct is provided, use it for unpacking
            elif struct_format:
                for item in field_value:
                    result += struct_format.pack(item)

            # Else bail
            else:
                raise ValueError('Missing structure definition for list field', field_name)

        # Else use the struct for packing if available
        if struct_format:
            result += struct_format.pack(field_value)

        # If it's a dataclass, recursively serialize it
        elif isinstance(field_value, BaseBinary):
            result += field_value.to_bytes()

        # If it's a string, encode it and null terminate it
        elif isinstance(field_value, str):
            result += field_value.encode('ascii') + b'\0'

        # Add alignment padding and return result
        result = pad(result, field_meta[ALIGN_PAD])
        return result

    @final
    def field_from_json(self, field: Union[Field, str], data: dict) -> None:
        """
        Deserializes a field from a JSON-like dictionary. Does not return anything.
        """

        # Get the field if a string is passed
        if type(field) == str:
            field = self.__dataclass_fields__[field]

        # Get the field information
        field_name = field.name
        field_type = field.type
        field_default = field.default
        field_default_factory = field.default_factory
        field_meta = field.metadata

        # Convert the field name
        field_json_name = snake_to_camel(field_name)

        # Check if the data is there
        if field_json_name in data or field_meta[UNROLL_CONTENT]:

            # If it's a dataclass, construct it recursively
            if issubclass(field_type, BaseBinary):

                # Use the same dict if unrolled
                if field_meta[UNROLL_CONTENT]:
                    setattr(self, field_name, field_type.from_json(data, self))
                else:
                    setattr(self, field_name, field_type.from_json(data[field_json_name], self))

            # For lists, ensure it's a list and parse it
            elif get_origin(field_type) == list:
                if not isinstance(data[field_json_name], list):
                    raise TypeError(f'Expected a list for field {field_name}')

                # Check if the underlying type is a dataclass or not
                list_type = field_type.__args__[0]
                if issubclass(list_type, BaseBinary):
                    setattr(self, field_name, [list_type.from_json(value, self) for value in data[field_json_name]])
                else:
                    setattr(self, field_name, data[field_json_name])

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
                setattr(self, field_name, value)

            # For enums, convert from string
            elif issubclass(field_type, Enum):

                # Ensure value is a string
                value = data[field_json_name]
                if not isinstance(value, str):
                    raise TypeError(f'Expected a string for field {field_name}')

                # Set it
                setattr(self, field_name, field_type[value])

            # Else verify the type matches the expected one, and if so set it
            else:
                value = data[field_json_name]
                if not isinstance(value, field_type):
                    raise TypeError(f'Expected type {field_type} for field {field_name}')

                # If valid, set it
                setattr(self, field_name, value)

        # If not found, try using the default value
        elif field_default is not MISSING:
            setattr(self, field_name, field_default)

        # Try also the default factory
        elif field_default_factory is not MISSING:
            setattr(self, field_name, field_default_factory())

        # Else just bail
        else:
            raise ValueError(f'Missing value for field {field_name}')

    @final
    def field_to_json(self, field: Union[Field, str]) -> dict:
        """
        Serializes a field to a JSON-like dictionary. Returns the serialized data.
        """

        # Get the field if a string is passed
        if type(field) == str:
            field = self.__dataclass_fields__[field]

        # Get info
        field_name = field.name
        field_meta = field.metadata
        field_type = field.type

        # Initialize result
        result = {}

        # Convert the field name
        field_json_name = snake_to_camel(field_name)

        # Get the value
        field_value = getattr(self, field_name)

        # If it's a dataclass, convert it to dictionary using its method
        if isinstance(field_value, BaseBinary):
            value = field_value.to_json()

            # If it needs to be unrolled, simply merge the result into the given dictionary
            if field_meta[UNROLL_CONTENT]:
                result |= value

            # Else just store it under the key
            else:
                result[field_json_name] = value

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

        # Return the result
        return result

    @final
    def field_size(self, field: Union[Field, str]):
        """
        Gets the size of a field.
        """

        # Get the field if a string is passed
        if type(field) == str:
            field = self.__dataclass_fields__[field]

        # Get field data
        field_name = field.name
        field_meta = field.metadata
        field_value = getattr(self, field_name)

        # Initialize size
        size = 0

        # Get struct format
        struct_format: struct.Struct = field_meta[STRUCT]

        # If it's a list, calculate the size iteratively
        if isinstance(field_value, list):

            # Get the list's contained type
            list_type = field.type.__args__[0]

            # If the contained data is a dataclass, iteratively sum it
            if isinstance(list_type, type) and issubclass(list_type, BaseBinary):
                for item in field_value:
                    size += item.size()

            # Else if a struct is provided, use it for the calculation
            elif struct_format:
                for item in field_value:
                    size += struct_format.size

            # Else bail
            else:
                raise ValueError('Missing structure definition for list field', field_name)

        # If a structure is given, use it
        elif struct_format:
            size += struct_format.size

        # For dataclasses, use the size method recursively
        elif isinstance(field_value, BaseBinary):
            size += field_value.size()

        # For strings, calculate the length
        elif isinstance(field_value, str):
            size += len(field_value) + 1

        # Align size and return it
        size = align(size, field_meta[ALIGN_PAD])
        return size

    @classmethod
    def from_bytes(cls: Type[T], data: bytes, offset: int = 0, parent: Optional[T] = None) -> T:
        """
        Deserializes the type from a byte sequence.
        """

        # Create the class and set the parent
        obj = cls()
        obj.parent = parent

        # Iterate the class fields
        for field in fields(cls):

            # If the field is marked as ignored, skip it
            if field.metadata[IGNORE_BINARY]:
                continue

            # Decode the field and validate it
            offset = obj.field_from_bytes(field, data, offset)
            obj.validate(len(data), field)

        # Return the finished object
        return obj

    def to_bytes(self) -> bytes:
        """
        Serializes the type to a byte sequence.
        """

        # Initialize result
        result = b''

        # Iterate the class fields
        for field in fields(self):
            if not field.metadata[IGNORE_BINARY]:
                result += self.field_to_bytes(field)

        # Return final result
        return result

    @classmethod
    def from_json(cls: Type[T], data: dict, parent: Optional[T] = None) -> T:
        """
        Deserializes the type from a JSON-like dictionary.
        """

        # Create the class and set the parent
        obj = cls()
        obj.parent = parent

        # Parse each field
        for field in fields(cls):
            if not field.metadata[IGNORE_JSON]:
                obj.field_from_json(field, data)

        # Return built object
        return obj

    def to_json(self) -> dict:
        """
        Serializes the type to a JSON-like dictionary.
        """

        # Initialize the result
        result = {}

        # Parse each field
        for field in fields(self):
            if not field.metadata[IGNORE_JSON]:
                result |= self.field_to_json(field)

        # Return resulting dict
        return result

    def size(self, end_field: str = None) -> int:
        """
        Get the size of the data until end_field (inclusive).
        Pass None to compute the size of the entire structure.
        Fields with ignore_binary set to True will be skipped.
        """

        # Initialize loop
        size = 0

        # Sum each field size
        for field in fields(self):

            # Update size
            if not field.metadata[IGNORE_BINARY]:
                size += self.field_size(field)

            # If we have reached the last field, exit the loop
            if field.name == end_field:
                break

        # Return result
        return size

    def validate(self, data_length: int, field: Field) -> None:
        """
        Validates the data for the given field.
        """
        return
