#!/usr/bin/env python3

# anim_table.py
# Animation table definitions

from dataclasses import dataclass
from common.common import BaseBinary, fieldex

@dataclass
class AnimationTable(BaseBinary):
    anim_count: int = fieldex('H')
    init_anim_count: int = fieldex('H')
    anim_ptrs: list[int] = fieldex('I', ignore_json=True, count_field='anim_count')
    anim_sizes: list[int] = fieldex('I', ignore_json=True, count_field='anim_count')


@dataclass
class NameTableEntry(BaseBinary):
    name_len: int = fieldex('H', ignore_json=True)
    name: str = fieldex()

    def to_bytes(self) -> bytes:
        self.name_len = len(self.name) + 1
        return super().to_bytes()


@dataclass
class NameTable(BaseBinary):
    name_table_size: int = fieldex('H2x')
    name_ptrs: list[int] = fieldex('I', ignore_json=True, count_field='name_table_size')
    names: list[NameTableEntry] = fieldex(count_field='name_table_size')

    def to_bytes(self) -> bytes:
        self.name_ptrs = [0] * len(self.names)
        self.name_table_size = len(self.names)
        return super().to_bytes()
