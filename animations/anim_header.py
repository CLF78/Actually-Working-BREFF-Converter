#!/usr/bin/env python3

# anim_base.py
# Base animation definitions

from dataclasses import dataclass
from common.common import BaseBinary, fieldex
from animations.anim_flags import *
from animations.anim_child import AnimationChild

@dataclass
class AnimationHeader(BaseBinary):
    is_init: bool = fieldex(ignore_binary=True)
    is_baked: bool = fieldex(ignore_binary=True)

    magic: int = fieldex('B', ignore_json=True)
    kind_type: int = fieldex('B', ignore_json=True)
    curve_type: AnimType = fieldex('B', ignore_json=True)
    kind_enable: int = fieldex('B', ignore_json=True)

    # Stupid ass workaround for Python's inability to properly handle duplicate enum values
    target: str = fieldex(ignore_binary=True)

    process_flag: AnimProcessFlag = fieldex('B')
    loop_count: int = fieldex('B')
    random_seed: int = fieldex('H')
    frame_length: int = fieldex('H2x')

    # TODO remove these from the JSON
    key_table_size: int = fieldex('I')
    range_table_size: int = fieldex('I')
    random_table_size: int = fieldex('I')
    name_table_size: int = fieldex('I')
    info_table_size: int = fieldex('I')

    # The actual data depends on the curve type, so it's handled manually
    data: BaseBinary = fieldex(ignore_binary=True, ignore_json=True)

    @classmethod
    def from_bytes(cls, data: bytes, offset: int = 0, parent = None) -> 'AnimationHeader':

        # Decode the header
        ret = super().from_bytes(data, offset, parent)
        offset += ret.size('info_table_size')

        # Decode target because we need it for decoding the rest
        target = get_target_from_type(ret.curve_type, ret.kind_type)

        # Create the data
        match target:

            case AnimTargetChild.Child:
                ret.data = AnimationChild.from_bytes(data, offset, ret)

            # We cannot parse this animation type yet, so ignore it
            case _:
                #print('Skipping data for animation type', ret.target, 'because we cannot parse it yet.')
                ret.data = BaseBinary.from_bytes(data, offset, ret)

        # Return data
        ret.target = target.name
        return ret

    def to_bytes(self) -> bytes:

        # Set values
        self.magic = 0xAB if self.is_baked else 0xAC
        target = get_target_from_string(self.target)
        self.kind_type = target.value
        self.curve_type = get_type_from_target(target, self.is_baked)

        # Ensure data is encoded first to adjust table sizes
        data = self.data.to_bytes()
        return super().to_bytes() + data

    @classmethod
    def from_json(cls, data: dict, parent = None) -> 'AnimationHeader':

        # Parse the header data and get the target, required to parse the rest of the data
        ret = super().from_json(data, parent)
        target = get_target_from_string(ret.target)

        # Create the data
        match target:
            case AnimTargetChild.Child:
                ret.data = AnimationChild.from_json(data, ret)

            # We cannot parse this animation type yet, so ignore it
            case _:
                #print('Skipping data for animation type', ret.target, 'because we cannot parse it yet.')
                ret.data = BaseBinary.from_json(data, ret)

        # Return data
        return ret

    def to_json(self) -> dict:
        self.is_baked = self.magic == 0xAB
        return super().to_json() | self.data.to_json()

    def size(self, end_field: str = None) -> int:
        size = super().size(end_field if end_field else 'info_table_size')

        if end_field is None:
            size += self.key_table_size + self.range_table_size + self.random_table_size + \
                    self.name_table_size + self.info_table_size

        return size
