#!/usr/bin/env python3

# anim_table.py
# Animation table definition

from dataclasses import dataclass
from common.common import BaseBinary, fieldex

@dataclass
class AnimationTable(BaseBinary):
    anim_count: int = fieldex('H')
    init_anim_count: int = fieldex('H')
    anim_ptrs: list[int] = fieldex('I', ignore_json=True, count_field='anim_count')
    anim_sizes: list[int] = fieldex('I', ignore_json=True, count_field='anim_count')
