#!/usr/bin/env python3

# field.py
# Base field definitions.

import struct
from enum import IntEnum, IntFlag
from typing import Any, Callable, Callable, Optional, Type, TypeVar
from common.common import align, pad, snake_to_camel, pascal_to_camel, camel_to_pascal, printv

####################
# Type Definitions #
####################

S = TypeVar('S', bound='Structure')
F = TypeVar('F', bound='Field')

# Field container
FieldDict = dict[str, 'Field']
FIELD_LIST = '_fields_'

# Function to determine whether the field should be skipped
FieldCondition = Callable[['Structure'], bool]

# Function or field to determine the length of a field (or integer to use a fixed length)
FieldLength = int | F | Callable[['Structure'], int]

# Function to determine the type of a field
FieldTypeSelector = Callable[['Structure', bool], 'Field']

# Base cond functions
def skip_json(structure: 'Structure', is_json: bool):
    return not is_json

def skip_binary(structure: 'Structure', is_json: bool):
    return is_json

def skip_all(structure: 'Structure', is_json: bool):
    return False

###############
# Field Types #
###############

class Field:
    """
    Represents a field.
    """
    def __init__(self, fmt: str, default: Any = None, default_factory: Optional[Callable] = None,
                 alignment: int = 1, cond: Optional[FieldCondition] = None) -> None:
        """
        Initializes the field.

        :param fmt: The struct format used to unpack/pack the field. Set to an empty string for fields that do not use this.
        :param default: The default value for the field, defaults to None.
        :param default_factory: The default factory for the field, has precedent over default and defaults to None.
        :param alignment: How many bytes the next field should be aligned by, defaults to 1.
        :param cond: The condition to be verified to parse/export the field, defaults to None.
        """
        self.fmt = f'>{fmt}'
        self.default = default
        self.default_factory = default_factory
        self.alignment = alignment
        self.cond = cond
        self.private_name = ''

    def from_bytes(self, data: bytes, offset: int, parent: Optional['Structure'] = None) -> tuple[Any, int]:
        """
        Converts the field from its binary representation.
        :param data: The data to be converted.
        :param offset: The offset to read the data from.
        :return: A tuple of the decoded data and the updated offset.
        """
        size = self.size()
        value = struct.unpack_from(self.fmt, data, offset)[0]
        return value, offset + size

    def decode(self, value: Any) -> None:
        """
        Does additional preprocessing before decoding the data.
        :param value: The data to be decoded.
        """
        return

    def to_bytes(self, value: Any) -> bytes:
        """
        Converts the field to its binary representation.
        :param value: The data to be converted.
        :return: The converted data.
        """
        return struct.pack(self.fmt, value)

    def from_json(self, value: Any, parent: Optional['Structure'] = None) -> Any:
        """
        Converts the field from its JSON representation.
        :param value: The data to be converted.
        :return: The converted data.
        """
        return value

    def encode(self, value: Any) -> None:
        """
        Does additional preprocessing before encoding the data.
        :param value: The data to be encoded.
        """
        return

    def to_json(self, value: Any) -> Any:
        """
        Converts the field to its JSON representation.
        :param value: The data to be converted.
        :return: The converted data.
        """
        return value

    def size(self, instance: Any = None) -> int:
        """
        Calculates the size of the field.
        :param instance: The instance of the field, for fields that require the value to calculate the size.
        :return: The calculated size.
        """
        return struct.calcsize(self.fmt)


class StructureMeta(type):
    def __new__(cls, name: str, bases: tuple, class_dict: dict[str, Any]):

        # Get the base class fields
        fields: FieldDict = {}
        for base in bases:
            if hasattr(base, FIELD_LIST):
                fields.update(base._fields_)

        # Add the class' own fields
        for k, v in class_dict.items():
            if isinstance(v, Field):
                fields[k] = v
                v.private_name = k

        # Continue
        class_dict[FIELD_LIST] = fields
        return super().__new__(cls, name, bases, class_dict)


class Structure(metaclass=StructureMeta):
    def __init__(self, parent: Optional['Structure'] = None):
        self.parent = parent

        # Copy the field dictionary and set the default for each field
        # This is necessary to account for fields that change depending on the context (like UnionFields)
        fields = self._fields_
        self._fields_: FieldDict = dict.copy(fields)
        for name, field in fields.items():
            if field.default_factory:
                setattr(self, name, field.default_factory())
            else:
                setattr(self, name, field.default)

    @classmethod
    def from_bytes(cls, data: bytes, offset: int = 0, parent: Optional['Structure'] = None) -> tuple['Structure', int]:
        instance = cls(parent)
        offset = instance._from_bytes(data, offset)
        return instance, offset

    def _from_bytes(self, data: bytes, offset: int = 0) -> int:
        for name, field in self._fields_.items():

            # Skip field if cond does not match
            if field.cond and not field.cond(self, False):
                continue

            # Decode field and update offset
            printv(f'Decoding field {name} (type {type(field).__name__}) at offset {hex(offset)}')
            value, offset = field.from_bytes(data, offset, self)
            setattr(self, name, value)

            # Align offset
            offset = align(offset, field.alignment)

        # Return updated offset
        return offset

    def decode(self) -> None:
        for name, field in self._fields_.items():

            # Skip field if cond does not match
            if field.cond and not field.cond(self, True):
                continue

            # Run encode otherwise
            field.decode(getattr(self, name))

    def to_json(self) -> dict[str, Any]:

        # If this is a root structure, do the decode step first
        if self.parent is None:
            self.decode()

        # Set up loop
        result = {}
        for name, field in self._fields_.items():

            # Skip field if cond does not match
            if field.cond and not field.cond(self, True):
                continue

            # Get value and convert it
            printv(f'Encoding field {name} (type {type(field).__name__})')
            value = getattr(self, name)
            json_value = field.to_json(value)

            # Insert it directly if unrolled
            if isinstance(field, StructField) and field.unroll:
                result.update(json_value)
            else:
                result[snake_to_camel(name)] = json_value

        # Return result
        return result

    @classmethod
    def from_json(cls, data: dict[str, Any], parent: Optional['Structure'] = None) -> 'Structure':
        instance = cls(parent)
        instance._from_json(data)
        return instance

    def _from_json(self, data: dict[str, Any]) -> None:
        for name, field in self._fields_.items():
            printv(f'Decoding field {name} (type {type(field).__name__})')

            # Defer decoding for UnionField since we don't know the underlying data structure at this stage
            if (isinstance(field, StructField) and field.unroll) or isinstance(field, UnionField):
                setattr(self, name, field.from_json(data, self))

            # Ignore conditions and read every field regardless
            # This is not safe as the user can override default/calculated values, but if the resulting
            # file is corrupted the user can be safely blamed for the error
            elif (key := snake_to_camel(name)) in data:
                setattr(self, name, field.from_json(data[key], self))

    def encode(self) -> None:
        for name, field in self._fields_.items():

            # Skip field if cond does not match
            if field.cond and not field.cond(self, False):
                continue

            # Run encode otherwise
            field.encode(getattr(self, name))

    def to_bytes(self) -> bytes:

        # If this is a root structure, do the encode step first
        if self.parent is None:
            self.encode()

        # Set up loop
        result = b''
        for name, field in self._fields_.items():

            # Skip field if cond does not match
            if field.cond and not field.cond(self, False):
                continue

            # Encode field and add necessary padding
            value = getattr(self, name)
            printv(f'Encoding field {name} (type {type(field).__name__}) = {value}')
            result += field.to_bytes(value)
            result = pad(result, field.alignment)

        # Return result
        return result

    def size(self, start_field: Optional[F] = None, end_field: Optional[F] = None) -> int:

        # Set up loop
        result = 0
        found_start = start_field is None
        for field in self._fields_.values():

            # Find the starting field
            if start_field and field.private_name == start_field.private_name:
                found_start = True

            # Calculate the size
            # Use binary conditions as sizes are irrelevant in the deserialized version
            if found_start and (field.cond is None or field.cond(self, False)):
                result += field.size(self)
                result = align(result, field.alignment)

            # Find the end field
            if end_field and field.private_name == end_field.private_name:
                break

        # Return result
        return result

    def get_parent(self, parent_type: Type[S]) -> S:
        current = self
        while current:
            if isinstance(current, parent_type):
                return current
            current = current.parent
        raise ValueError(f'No parent of type {parent_type.__name__} found')


class padding(Field):
    def __init__(self, length: int) -> None:
        super().__init__(f'{length}x', default=0, cond=skip_json)

    def from_bytes(self, data: bytes, offset: int, parent: Optional[Structure] = None) -> tuple[int, int]:
        size = struct.calcsize(self.fmt)
        return 0, offset + size

    def to_bytes(self, value: Any) -> bytes:
        return struct.pack(self.fmt)


class s8(Field):
    def __init__(self, fmt: str = 'b', **kwargs) -> None:
        super().__init__(fmt, **kwargs)


class u8(Field):
    def __init__(self, fmt: str = 'B', **kwargs) -> None:
        super().__init__(fmt, **kwargs)


class s16(Field):
    def __init__(self, fmt: str = 'h', **kwargs) -> None:
        super().__init__(fmt, **kwargs)


class u16(Field):
    def __init__(self, fmt: str = 'H', **kwargs) -> None:
        super().__init__(fmt, **kwargs)


class s32(Field):
    def __init__(self, fmt: str = 'i', **kwargs) -> None:
        super().__init__(fmt, **kwargs)


class u32(Field):
    def __init__(self, fmt: str = 'I', **kwargs) -> None:
        super().__init__(fmt, **kwargs)


class u64(Field):
    def __init__(self, fmt: str = 'Q', **kwargs) -> None:
        super().__init__(fmt, **kwargs)


class f32(Field):
    def __init__(self, fmt: str = 'f', **kwargs) -> None:
        super().__init__(fmt, **kwargs)


class boolean(Field):
    def __init__(self, fmt: str = '?', **kwargs) -> None:
        super().__init__(fmt, **kwargs)


class raw(Field):
    def __init__(self, length: FieldLength = 0, **kwargs) -> None:
        super().__init__('', **kwargs)
        self.length = length

    def from_bytes(self, data: bytes, offset: int, parent: Optional[Structure] = None) -> tuple[bytes, int]:
        length = self.length
        if callable(self.length):
            length = self.length(parent)
        elif isinstance(self.length, Field):
            length = getattr(parent, self.length.private_name)

        end = offset + length
        return data[offset:end], end

    def to_bytes(self, value: bytes) -> bytes:
        return value

    def size(self, instance: Any = None) -> int:
        return len(getattr(instance, self.private_name, b''))


class string(Field):
    def __init__(self, **kwargs) -> None:
        super().__init__('', **kwargs)

    def from_bytes(self, data: bytes, offset: int, parent: Optional[Structure] = None) -> tuple[str, int]:
        end = data.index(b'\0', offset)
        value = data[offset:end].decode('ascii')
        return value, end + 1

    def to_bytes(self, value: str) -> bytes:
        return value.encode('ascii') + b'\0'

    def size(self, instance: Any = None) -> int:
        value = getattr(instance, self.private_name, '')
        return len(value) + 1


class EnumField(Field):
    def __init__(self, enum_type: Type[IntEnum], fmt: str = 'B', mask: int | IntEnum = -1, **kwargs) -> None:
        super().__init__(fmt, **kwargs)
        self.enum_type = enum_type
        self.mask = mask

    def from_bytes(self, data: bytes, offset: int, parent: Optional[Structure] = None) -> tuple[IntEnum, int]:
        value, offset = super().from_bytes(data, offset, parent)
        return self.enum_type(value & self.mask), offset

    def to_json(self, value: IntEnum) -> str:
        return value.name

    def from_json(self, value: str, parent: Optional[Structure] = None) -> IntEnum:
        return self.enum_type(self.enum_type[value] & self.mask)

    def to_bytes(self, value: IntEnum) -> bytes:
        return super().to_bytes(value.value)


class FlagEnumField(EnumField):
    def __init__(self, enum_type: Type[IntFlag], fmt: str = 'B', mask: int | IntFlag = -1, **kwargs) -> None:
        super().__init__(enum_type, fmt, mask, **kwargs)

    def to_json(self, value: IntFlag) -> dict[str, bool]:
        result = {}
        for flag in self.enum_type:
            result[pascal_to_camel(flag.name)] = bool(flag & value)
        return result

    def from_json(self, value: dict[str, bool], parent: Optional[Structure] = None) -> IntFlag:
        result = self.enum_type(self.default if self.default else 0)
        for flag_name, is_set in value.items():
            if is_set:
                result |= self.enum_type[camel_to_pascal(flag_name)]
        return result


class StructField(Field):
    def __init__(self, struct_type: Type[Structure], unroll: bool = False, **kwargs) -> None:
        super().__init__('', default=None, **kwargs)
        self.struct_type = struct_type
        self.unroll = unroll

    def from_bytes(self, data: bytes, offset: int, parent: Optional[Structure] = None) -> tuple[Structure, int]:
        return self.struct_type.from_bytes(data, offset, parent)

    def decode(self, value: Structure) -> None:
        value.decode() if value else None

    def to_json(self, value: Structure) -> dict[str, Any]:
        return value.to_json() if value else {}

    def from_json(self, value: dict[str, Any], parent: Optional[Structure] = None) -> Structure:
        return self.struct_type.from_json(value, parent)

    def encode(self, value: Structure) -> None:
        value.encode() if value else None

    def to_bytes(self, value: Structure) -> bytes:
        return value.to_bytes() if value else b''

    def size(self, instance: Optional[Structure] = None) -> int:
        return getattr(instance, self.private_name).size() if instance else 0


class UnionField(Field):
    def __init__(self, type_selector: FieldTypeSelector, **kwargs) -> None:
        super().__init__('', default=None, default_factory=None, **kwargs)
        self.type_selector = type_selector

    def detect_field(self, parent: Structure, is_json: bool) -> Field:
        selected_field = self.type_selector(parent, is_json)
        parent._fields_[self.private_name] = selected_field
        selected_field.private_name = self.private_name
        return selected_field

    def from_bytes(self, data: bytes, offset: int, parent: Optional[Structure] = None) -> tuple[Any, int]:
        if not parent:
            raise ValueError('A parent is required for decoding a UnionField!')
        return self.detect_field(parent, False).from_bytes(data, offset, parent)

    def decode(self, value: Structure) -> None:
        raise NotImplementedError('UnionField should not call decode() directly; it must be replaced by the selected field.')

    def to_json(self, value: Any) -> Any:
        raise NotImplementedError('UnionField should not call to_json() directly; it must be replaced by the selected field.')

    def from_json(self, value: Any, parent: Optional[Structure] = None) -> Any:
        if not parent:
            raise ValueError('A parent is required for decoding a UnionField!')

        # Deferred data decoding
        field = self.detect_field(parent, True)
        if isinstance(field, StructField) and field.unroll:
            return field.from_json(value, parent)
        elif (key := snake_to_camel(self.private_name)) in value:
            return field.from_json(value[key], self)
        return None

    def encode(self, value: Structure) -> None:
        raise NotImplementedError('UnionField should not call encode() directly; it must be replaced by the selected field.')

    def to_bytes(self, value: Any) -> bytes:
        raise NotImplementedError('UnionField should not call to_bytes() directly; it must be replaced by the selected field.')

    def size(self, instance: Optional[Structure] = None) -> int:
        raise NotImplementedError('UnionField should not call size() directly; it must be replaced by the selected field.')


class ListField(Field):
    def __init__(self, item_field: F, length: FieldLength = 0, default_factory=list, **kwargs) -> None:
        super().__init__('', None, default_factory, **kwargs)
        self.item_field = item_field
        self.length = length

    def from_bytes(self, data: bytes, offset: int, parent: Optional[Structure] = None) -> tuple[list, int]:

        # Ensure parent exists
        if not parent:
            raise ValueError('A parent is required for decoding a ListField!')

        # Get the length
        length = self.length
        if callable(self.length):
            length = self.length(parent)
        elif isinstance(self.length, Field):
            length = getattr(parent, self.length.private_name)

        # Parsing loop
        value = []
        for _ in range(length):
            item, offset = self.item_field.from_bytes(data, offset, parent)
            value.append(item)

        # Return the final list along with the offset
        return value, offset

    def decode(self, value: list) -> None:
        value = value if value else []
        for item in value:
            self.item_field.decode(item)

    def to_json(self, value: list) -> list[Any]:
        return [self.item_field.to_json(item) for item in value]

    def from_json(self, value: list, parent: Optional[Structure] = None) -> list:
        return [self.item_field.from_json(item, parent) for item in value]

    def encode(self, value: list) -> None:
        value = value if value else []
        for item in value:
            self.item_field.encode(item)

    def to_bytes(self, value: list) -> bytes:
        return b''.join(self.item_field.to_bytes(item) for item in value)

    def size(self, instance: Any = None) -> int:
        result = 0
        value: list = getattr(instance, self.private_name)
        for item in value:
            result += self.item_field.size(item)
        return result
