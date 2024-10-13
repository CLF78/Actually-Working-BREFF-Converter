#!/usr/bin/env python3

# header.py
# Animation header definition

from dataclasses import dataclass
from common.common import BaseBinary, fieldex
from animations.flags import *

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

    def to_bytes(self) -> bytes:

        # Set values
        self.magic = 0xAB if self.is_baked else 0xAC
        target = get_target_from_string(self.target)
        self.kind_type = target.value
        self.curve_type = get_type_from_target(target, self.is_baked)
        return super().to_bytes()

    def to_json(self) -> dict:
        self.is_baked = self.magic == 0xAB
        self.target = get_target_from_type(self.curve_type, self.kind_type)
        return super().to_json()

    def size(self, end_field: str = None) -> int:
        size = super().size(end_field if end_field else 'info_table_size')

        if end_field is None:
            size += self.key_table_size + self.range_table_size + self.random_table_size + \
                    self.name_table_size + self.info_table_size

        return size
