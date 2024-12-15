#!/usr/bin/env python3

# child.py
# Child animation definitions

from enum import IntFlag, auto
from typing import Any
from common.common import CEnum
from common.field import *
from animations.common import *
from animations.tables import *


class ChildType(CEnum):
    Particle = auto()
    Emitter = auto()


class ChildFlag(IntFlag):
    FollowEmitter   = 1 << 0 # Unused
    InheritRotation = 1 << 1


class AlphaInheritanceFlag(IntFlag):
    PrimaryAlpha          = 1 << 0
    SecondaryAlpha        = 1 << 1
    AlphaFlickAndModifier = 1 << 2


class AnimationChildParam(Structure):
    name = string(cond=skip_binary)
    speed = s16() # Used for all axes
    scale = u8() # Used for all axes
    alpha = u8() # Used for both primary and secondary
    color = u8() # Used for all color channels, both primary and secondary
    render_priority = u8(default=128)
    child_type = EnumField(ChildType)
    child_flags = FlagEnumField(ChildFlag)
    alpha_primary_sources = FlagEnumField(AlphaInheritanceFlag)
    alpha_secondary_sources = FlagEnumField(AlphaInheritanceFlag)
    name_idx = u16(cond=skip_json)

    def to_json(self) -> dict[str, Any]:
        self.name = self.get_parent(AnimationChild).name_table.names[self.name_idx].name
        return super().to_json()


# Used as part of the randomization algorithm, value is the index into the key list
class AnimationChildRandomKey(Structure):
    idx = u16('H10x', cond=skip_json)


class AnimationChildKeyFrame(KeyFrameBase):
    def get_frame_data(self) -> Field:
        if self.value_type == KeyType.Random:
            return StructField(AnimationChildRandomKey, True)
        else:
            return StructField(AnimationChildParam, True)

    padd = padding(8)
    data = UnionField(get_frame_data)


class AnimationChild(Structure):
    def get_key_count(self) -> int:
        return self.frame_table.entry_count

    def has_random_table(self, is_json: bool) -> bool:
        return not is_json and get_anim_header(self).random_table_size != 0

    def has_random_pool(self, is_json: bool) -> bool:
        return is_json or self.has_random_table(is_json)

    def get_random_count(self) -> int:
        return self.random_table.entry_count

    frame_table = StructField(AnimDataTable, cond=skip_json)
    frames = ListField(StructField(AnimationChildKeyFrame), get_key_count)
    random_table = StructField(AnimDataTable, cond=has_random_table)
    random_pool = ListField(StructField(AnimationChildParam), get_random_count, cond=has_random_pool)
    name_table = StructField(NameTable, alignment=4, cond=skip_json)
