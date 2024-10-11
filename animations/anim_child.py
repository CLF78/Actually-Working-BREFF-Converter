#!/usr/bin/env python3

# anim_child.py
# Child animation definition

from dataclasses import dataclass
from typing import Optional, Type
from common.common import BaseBinary, fieldex

@dataclass
class AnimationChildFrame(BaseBinary):
    frame: int = fieldex('H')
    name: str = fieldex(ignore_binary=True)

    # TODO figure out what the fuck these mean
    flag: int = fieldex('Bx')
    curve_types: int = fieldex('Q')

    # These may not be correct if randomized, but i'm not certain
    speed: int = fieldex('h')
    scale: int = fieldex('B')
    alpha: int = fieldex('B')
    color: int = fieldex('B')
    weight: int = fieldex('B')
    inherit_type: int = fieldex('B')
    inherit_flag: int = fieldex('B')
    alpha_func_pri: int = fieldex('B')
    alpha_func_sec: int = fieldex('B')
    name_idx: int = fieldex('H', ignore_json=True)


# TODO move elsewhere
@dataclass
class NameTableEntry(BaseBinary):
    name_len: int = fieldex('H', ignore_json=True)
    name: str = fieldex()

    def to_bytes(self) -> bytes:
        self.name_len = len(self.name) + 1
        return super().to_bytes()


# TODO move elsewhere
@dataclass
class NameTable(BaseBinary):
    name_table_size: int = fieldex('H2x')
    name_ptrs: list[int] = fieldex('I', ignore_json=True, count_field='name_table_size')
    names: list[NameTableEntry] = fieldex(count_field='name_table_size')

    def to_bytes(self) -> bytes:
        self.name_ptrs = [0] * len(self.names)
        self.name_table_size = len(self.names)
        return super().to_bytes()


@dataclass
class AnimationChild(BaseBinary):
    frame_table_size: int = fieldex('H2x', ignore_json=True)
    frames: list[AnimationChildFrame] = fieldex(count_field='frame_table_size')
    name_table: NameTable = fieldex(ignore_json=True)

    def to_bytes(self) -> bytes:
        self.frame_table_size = len(self.frames)
        for frame in self.frames:
            if frame.name not in self.name_table.names:
                self.name_table.names.append(frame.name)
            frame.name_idx = self.name_table.names.index(frame.name)

        return super().to_bytes()

    def to_json(self) -> dict:
        for frame in self.frames:
            frame.name = self.name_table.names[frame.name_idx].name
        return super().to_json()
