#!/usr/bin/env python3

# animation.py
# Base animation definitions

from dataclasses import dataclass
from common.common import BaseBinary, fieldex
from animations.anim_types import *

@dataclass
class AnimationBase(BaseBinary):
    is_init: bool = fieldex(ignore_binary=True)
    is_baked: bool = fieldex(ignore_binary=True)

    magic: int = fieldex('B', ignore_json=True)
    target: AnimTarget = fieldex('B')
    curve_type: AnimType = fieldex('B', ignore_json=True)
    kind_enable: int = fieldex('B')
    process_flag: AnimProcessFlag = fieldex('B')
    loop_count: int = fieldex('B')
    random_seed: int = fieldex('H')
    frame_length: int = fieldex('H2x')

    # TODO remove these from the JSON for known animation formats
    key_table_size: int = fieldex('I')
    range_table_size: int = fieldex('I')
    random_table_size: int = fieldex('I')
    name_table_size: int = fieldex('I')
    info_table_size: int = fieldex('I')

    def to_bytes(self) -> bytes:
        self.magic = 0xAB if self.is_baked else 0xAC
        self.curve_type = AnimType.get_from_target(self.target, self.is_baked)
        return super().to_bytes()

    def to_json(self) -> dict:
        self.is_baked = self.magic == 0xAB
        return super().to_json()
