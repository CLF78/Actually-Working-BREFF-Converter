#!/usr/bin/env python3

# u8.py
# Particle U8 animation definitions

from enum import Flag
from typing import Any
from common.field import *
from animations.tables.key import *

class AnimationColorTargets(Flag):
    Red   = 1 << 0
    Green = 1 << 1
    Blue  = 1 << 2


class AnimationOtherTargets(Flag):
    Main = 1 << 0


class AnimationU8KeyFixed(Structure):
    values = ListField(u8(), lambda x: 2 * x.parent.parent.parent.get_param_count())


class AnimationU8KeyRangeRandom(Structure):
    idx = u16('H2x')


class AnimationU8RangeValue(Structure):
    values = ListField(u8(), lambda x: 2 * x.parent.parent.get_param_count())


def get_key_data(key: Structure) -> Field:
    key: AnimationU8Key = key
    if key.base.value_type == KeyType.Fixed:
        return StructField(AnimationU8KeyFixed, True)
    else:
        return StructField(AnimationU8KeyRangeRandom, True)


class AnimationU8Key(Structure):
    base = StructField(KeyFrameBase, True)
    curve_types = ListField(EnumField(KeyCurveType), lambda x: x.parent.parent.get_param_count())
    padd = ListField(u8(), lambda x: 8 - x.parent.parent.get_param_count(), skip_json=True)
    key_data = UnionField(get_key_data)
    # Key type 0:
    # - Couple of u8s for each enabled target
    # Key type 1:
    # - Range table index u16 + 2 bytes padding
    # Key type 2:
    # - Random table seed u16 + 2 bytes padding


class AnimationU8BeautifiedTarget(Structure):
    interp_type = EnumField(KeyCurveType)
    values = ListField(u8(), 2, cond=lambda x: x.parent.value_type != KeyType.Random)


class AnimationU8BeautifiedFrame(Structure):
    frame = u16()
    value_type = EnumField(KeyType)
    targets = ListField(AnimationU8BeautifiedTarget, 1)
    random_seed = u16(cond=lambda x: x.value_type == KeyType.Random)


# TODO finish and beautify format
class AnimationU8(Structure):
    key_frame_table = StructField(KeyFrameTable, skip_json=True)
    key_frames = ListField(StructField(AnimationU8Key), lambda x: x.key_frame_table.entry_count, alignment=4, skip_json=True)
    range_table = StructField(KeyFrameTable, cond=lambda x: x.parent.range_table_size != 0, skip_json=True)
    range_values = ListField(StructField(AnimationU8RangeValue), lambda x: x.range_table.entry_count, cond=lambda x: x.parent.range_table_size != 0, alignment=4, skip_json=True)
    # Random table header (conditional)
    # Random entries (conditional, align by 4)

    def to_json(self) -> dict[str, Any]:
        return super().to_json()
