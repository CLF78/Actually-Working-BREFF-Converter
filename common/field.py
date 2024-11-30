import struct
from enum import Enum, Flag
from typing import Type, Callable, Any, Union, Optional
from common.common import align, pad, snake_to_camel

class Field:
    """
    Represents a field.
    """
    def __init__(self, fmt: str, default: Any = None, skip_binary: bool = False, skip_json: bool = False,
                 alignment: int = 1, cond: Optional[Callable[['Structure'], bool]] = None) -> None:
        """
        Initializes the field.

        :param fmt: The struct format used to unpack/pack the field. Set to an empty string for fields that do not use this.
        :param default: The default value for the field, defaults to None.
        :param skip_binary: Whether the field should be ignored when reading from / writing to binary, defaults to False.
        :param skip_json: Whether the field should be ignored when reading from / writing to JSON, defaults to False.
        :param alignment: How many bytes the next field should be aligned by, defaults to 1.
        :param cond: The condition to be verified to parse/export the field, defaults to None.
        """
        self.fmt = f'>{fmt}'
        self.default = default
        self.skip_binary = skip_binary
        self.skip_json = skip_json
        self.alignment = alignment
        self.cond = cond
        self.private_name = ''

    def __set_name__(self, owner: Any, name: str) -> None:
        self.private_name = f'_{name}'

    def __get__(self, instance: Any, owner: Any) -> Any:
        if instance is None:
            return self
        return getattr(instance, self.private_name)

    def __set__(self, instance: Any, value: Any) -> None:
        setattr(instance, self.private_name, value)

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
        if type(value) != type(self.default):
            raise TypeError('Type of field does not match expected format!')
        return value

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
        fields = {}
        for base in bases:
            a = getattr(base, '_fields_', {})
            print(base, a)
            fields.update(a)

        # Add the class' own fields
        fields.update({k: v for k, v in class_dict.items() if isinstance(v, Field)})

        # Set the private names and apply the dictionary
        for field_name, field in fields.items():
            field.__set_name__(cls, field_name)
        class_dict['_fields_'] = fields

        # Continue
        return super().__new__(cls, name, bases, class_dict)


class Structure(metaclass=StructureMeta):
    def __init__(self, parent: Optional['Structure'] = None):
        self.parent = parent

        # Copy the field dictionary and set the default for each contained field
        fields: dict[str, Field] = self._fields_ # type: ignore
        self._fields_ = dict.copy(fields)
        for name, field in fields.items():
            setattr(self, name, field.default)

    @classmethod
    def from_bytes(cls, data: bytes, offset: int = 0, parent: Optional['Structure'] = None) -> tuple['Structure', int]:
        instance = cls(parent)
        offset = instance._from_bytes(data, offset)
        return instance, offset

    def _from_bytes(self, data: bytes, offset: int = 0) -> int:

        # Set up loop
        fields: dict[str, Field] = self._fields_
        for name, field in fields.items():

            # Skip field if requested
            if field.skip_binary:
                continue

            # Skip field if cond does not match
            if field.cond and not field.cond(self):
                continue

            # TODO remove debug print
            print(name, type(field), hex(offset))

            # Decode field and update offset
            value, offset = field.from_bytes(data, offset, self)
            setattr(self, name, value)

            # Align offset
            offset = align(offset, field.alignment)

        # Return updated offset
        return offset

    def to_bytes(self) -> bytes:

        # Set up loop
        result = b''
        fields: dict[str, Field] = self._fields_
        for name, field in fields.items():

            # Skip field if requested
            if field.skip_binary:
                continue

            # Skip field if cond does not match
            if field.cond and not field.cond(self):
                continue

            # Encode field and add necessary padding
            result += field.to_bytes(getattr(self, name))
            result = pad(result, field.alignment)

        # Return result
        return result

    @classmethod
    def from_json(cls, data: dict[str, Any], parent: Optional['Structure'] = None) -> 'Structure':
        instance = cls(parent)
        instance._from_json(data)
        return instance

    def _from_json(self, data: dict[str, Any]) -> None:

        # Set up loop
        fields: dict[str, Field] = self._fields_
        for name, field in fields.items():

            # Skip if requested
            if field.skip_json:
                continue

            # Check if it's a nested structure
            if getattr(field, 'unroll', False):
                value = field.from_json(data, self)
            else:
                value = field.from_json(data[snake_to_camel(name)], self)

            # Set the value
            setattr(self, name, value)

    def to_json(self) -> dict[str, Any]:

        # Set up loop
        result = {}
        fields: dict[str, Field] = self._fields_
        for name, field in fields.items():

            # Skip if requested
            if field.skip_json:
                continue

            # Get value and encode it
            value = getattr(self, name)
            json_value = field.to_json(value)

            # Insert it directly if unrolled
            if getattr(field, 'unroll', False):
                result.update(json_value)
            else:
                result[snake_to_camel(name)] = json_value

        # Return result
        return result

    def size(self, start_field: Optional[Field] = None, end_field: Optional[Field] = None) -> int:

        # Set up loop
        result = 0
        found_start = start_field is None
        fields: dict[str, Field] = self._fields_
        for field in fields.values():

            # Find the starting field
            if start_field and field.private_name == start_field.private_name:
                found_start = True

            # Calculate the size
            if found_start and not field.skip_binary:
                result += field.size(self)
                result = align(result, field.alignment)

            # Find the end field
            if end_field and field.private_name == end_field.private_name:
                break

        # Return result
        return result


class padding(Field):
    def __init__(self, length: int) -> None:
        super().__init__(f'{length}x', default=0, skip_json=True)

    def from_bytes(self, data: bytes, offset: int, parent: Optional[Structure] = None) -> tuple[int, int]:
        size = struct.calcsize(self.fmt)
        return 0, offset + size

    def to_bytes(self, value: Any) -> bytes:
        return struct.pack(self.fmt)


class s8(Field):
    def __init__(self, fmt: str = 'b', default: int = 0, **kwargs) -> None:
        super().__init__(fmt, default, **kwargs)


class u8(Field):
    def __init__(self, fmt: str = 'B', default: int = 0, **kwargs) -> None:
        super().__init__(fmt, default, **kwargs)


class s16(Field):
    def __init__(self, fmt: str = 'h', default: int = 0, **kwargs) -> None:
        super().__init__(fmt, default, **kwargs)


class u16(Field):
    def __init__(self, fmt: str = 'H', default: int = 0, **kwargs) -> None:
        super().__init__(fmt, default, **kwargs)


class s32(Field):
    def __init__(self, fmt: str = 'i', default: int = 0, **kwargs) -> None:
        super().__init__(fmt, default, **kwargs)


class u32(Field):
    def __init__(self, fmt: str = 'I', default: int = 0, **kwargs) -> None:
        super().__init__(fmt, default, **kwargs)


class u64(Field):
    def __init__(self, fmt: str = 'Q', default: int = 0, **kwargs) -> None:
        super().__init__(fmt, default, **kwargs)


class f32(Field):
    def __init__(self, fmt: str = 'f', default: float = 0.0, **kwargs) -> None:
        super().__init__(fmt, default, **kwargs)


class boolean(Field):
    def __init__(self, fmt: str = '?', default: bool = False, **kwargs) -> None:
        super().__init__(fmt, default, **kwargs)


class raw(Field):
    def __init__(self, default: bytes = b'', length: Union[int, Callable] = 0, **kwargs) -> None:
        super().__init__('', default, **kwargs)
        self.length = length

    def from_bytes(self, data: bytes, offset: int, parent: Optional[Structure] = None) -> tuple[Any, int]:
        length = self.length(parent) if callable(self.length) else self.length
        end = offset + length
        return data[offset:end], end

    def to_bytes(self, value: bytes) -> bytes:
        return value

    def size(self, instance: Any = None) -> int:
        return len(getattr(instance, self.private_name, self.default))


class string(Field):
    def __init__(self, default: str = '', **kwargs) -> None:
        super().__init__('', default, **kwargs)

    def from_bytes(self, data: bytes, offset: int, parent: Optional[Structure] = None) -> tuple[str, int]:
        end = data.index(b'\0', offset)
        value = data[offset:end].decode('ascii')
        return value, end + 1

    def to_bytes(self, value: str) -> bytes:
        return value.encode('ascii') + b'\0'

    def size(self, instance: Any = None) -> int:
        value = getattr(instance, self.private_name, self.default)
        return len(value) + 1


class EnumField(Field):
    def __init__(self, enum_type: Type[Enum], fmt: str = 'B', default: int = 0, mask: int = -1, **kwargs) -> None:
        super().__init__(fmt, default, **kwargs)
        self.enum_type = enum_type
        self.mask = mask

    def from_bytes(self, data: bytes, offset: int, parent: Optional[Structure] = None) -> tuple[Any, int]:
        value, offset = super().from_bytes(data, offset, parent)
        return self.enum_type(value & self.mask), offset

    def to_bytes(self, value: Enum) -> bytes:
        return super().to_bytes(value.value)

    def from_json(self, value: str, parent: Optional[Structure] = None) -> Enum:
        return self.enum_type[value & self.mask]

    def to_json(self, value: Enum) -> str:
        return value.name


class FlagEnumField(EnumField):
    def __init__(self, enum_type: Type[Flag], fmt: str = 'B', default: int = 0, mask: int = -1, **kwargs) -> None:
        super().__init__(enum_type, fmt, default, mask, **kwargs)

    def from_json(self, value: dict[str, bool], parent: Optional[Structure] = None) -> Flag:
        result = self.enum_type(self.default)
        for flag_name, is_set in value.items():
            if is_set:
                result |= self.enum_type[flag_name].value
        return result

    def to_json(self, value: Flag) -> dict[str, bool]:
        result = {}
        for flag in self.enum_type:
            result[flag.name] = bool(flag & value)
        return result


class StructField(Field):
    def __init__(self, struct_type: Type[Structure], unroll: bool = False, **kwargs) -> None:
        super().__init__(fmt='', default=None, **kwargs)
        self.struct_type = struct_type
        self.unroll = unroll

    def from_bytes(self, data: bytes, offset: int, parent: Optional[Structure] = None) -> tuple[Structure, int]:
        return self.struct_type.from_bytes(data, offset, parent)

    def to_bytes(self, value: Structure) -> bytes:
        return value.to_bytes() if value else b''

    def from_json(self, value: dict[str, Any], parent: Optional[Structure] = None) -> Structure:
        return self.struct_type.from_json(value, parent)

    def to_json(self, value: Structure) -> dict[str, Any]:
        return value.to_json() if value else {}

    def size(self, instance: Optional[Structure] = None) -> int:
        return getattr(instance, self.private_name).size() if instance else 0


class UnionField(Field):
    def __init__(self, type_selector: Callable[[Structure], Field], **kwargs) -> None:
        super().__init__(fmt='', default=None, **kwargs)
        self.type_selector = type_selector

    def from_bytes(self, data: bytes, offset: int, parent: Optional[Structure] = None) -> tuple[Any, int]:
        # Ensure parent exists
        if not parent:
            raise ValueError('A parent is required for decoding a UnionField!')

        # Get the field and replace it if required
        selected_field = self.type_selector(parent)
        parent._fields_[self.private_name[1:]] = selected_field

        # Use the field for decoding
        return selected_field.from_bytes(data, offset, parent)

    def to_bytes(self, value: Any) -> bytes:
        raise NotImplementedError('UnionField should not call to_bytes() directly; it must be replaced by the selected field.')

    def from_json(self, value: Any, parent: Optional[Structure] = None) -> Any:

        # Ensure parent exists
        if not parent:
            raise ValueError('A parent is required for decoding a UnionField!')

        # Get the field and replace it if required
        selected_field = self.type_selector(parent)
        parent._fields_[self.private_name[1:]] = selected_field

        # Use the field for encoding
        return selected_field.from_json(value, parent)

    def to_json(self, value: Any) -> Any:
        raise NotImplementedError('UnionField should not call to_json() directly; it must be replaced by the selected field.')

    def size(self, instance: Optional[Structure] = None) -> int:
        raise NotImplementedError('UnionField should not call size() directly; it must be replaced by the selected field.')


class ListField(Field):
    current_item_field = '_reserved'

    def __init__(self, item_field: Field, counter: Union[int, Callable] = 0, **kwargs) -> None:
        super().__init__(fmt='', default=[], **kwargs)
        self.item_field = item_field
        self.counter = counter

        # Ensure this is set to avoid breaking UnionFields
        self.item_field.private_name = self.current_item_field

    def from_bytes(self, data: bytes, offset: int, parent: Optional[Structure] = None) -> tuple[list, int]:

        # Ensure parent exists
        if not parent:
            raise ValueError('A parent is required for decoding a ListField!')

        # Get the counter and initialize loop
        count = self.counter(parent) if callable(self.counter) else self.counter
        value = []
        for _ in range(count):

            # This is a work around for supporting UnionFields
            # Set a reserved field in the parent to store the field
            parent._fields_[self.current_item_field[1:]] = self.item_field

            # Get the item and offset
            item, offset = self.item_field.from_bytes(data, offset, parent)

            # If the field type was UnionField, this value has changed, so get it again and append it to the list
            # This allows us to decode the value later
            field_type = parent._fields_[self.current_item_field[1:]]
            value.append((field_type, item))

        # Remove the reserved field to prevent later breakage
        parent._fields_.pop(self.current_item_field[1:], None)

        # Return the final list along with the offset
        return value, offset

    def to_bytes(self, value: list[tuple[Field, Any]]) -> bytes:
        return b''.join(field.to_bytes(item) for field, item in value)

    def from_json(self, value: list, parent: Optional[Structure] = None) -> list:

        # Ensure parent exists
        if not parent:
            raise ValueError('A parent is required for decoding a ListField!')

        # Initialize loop
        data = []
        for item in value:

            # This is a work around for supporting UnionFields
            # Set a reserved field in the parent to store the field
            parent._fields_[self.current_item_field[1:]] = self.item_field

            # Get the item and offset
            item = self.item_field.from_json(item, parent)

            # If the field type was UnionField, this value has changed, so get it again and append it to the list
            # This allows us to encode the value later
            field_type = parent._fields_[self.current_item_field[1:]]
            data.append((field_type, item))

        # Remove the reserved field to prevent later breakage
        parent._fields_.pop(self.current_item_field[1:], None)

        # Return the updated list
        return data

    def to_json(self, value: list[tuple[Field, Any]]) -> list[Any]:
        return [field.to_json(item) for field, item in value]

    def size(self, instance: Any = None) -> int:
        result = 0
        value: list[tuple[Field, Any]] = getattr(instance, self.private_name, self.default)
        for field, item in value:
            result += field.size(item)
        return result
