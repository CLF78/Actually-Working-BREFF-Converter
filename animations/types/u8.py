#!/usr/bin/env python3

# u8.py
# Particle U8 animation definitions

from enum import IntFlag
from typing import Any
from common.field import *
from animations.tables import *
from animations.flags import *

###########
# Helpers #
###########

def get_anim_header(structure: Structure):
    from animations.header import AnimationHeader
    return structure.get_parent(AnimationHeader)

def get_param_count(structure: Structure) -> int:
    return get_anim_header(structure).get_param_count()

def get_key_type(structure: Structure) -> KeyType:
    return structure.get_parent(KeyFrameBase).value_type

def check_enabled_target(structure: Structure, target: IntFlag) -> bool:
    return (get_anim_header(structure).kind_enable & target) != 0

###########
# Targets #
###########

class AnimationU8ColorTargets(IntFlag):
    Red   = 1 << 0
    Green = 1 << 1
    Blue  = 1 << 2

class AnimationU8OtherTargets(IntFlag):
    Main = 1 << 0

###############
# Key Formats #
###############

class AnimationU8KeyFixed(Structure):
    values = ListField(u8(), get_param_count, alignment=2)

class AnimationU8KeyRangeRandom(Structure):
    def get_padding(self) -> int:
        param_count = get_anim_header(self).get_param_count()
        return align(0xC + param_count, 2) - 0xE

    idx = u16()
    padd = ListField(u8(), get_padding, cond=skip_json)


class AnimationU8Key(KeyFrameBase):
    def get_key_data(self) -> Field:
        if self.value_type == KeyType.Fixed:
            return StructField(AnimationU8KeyFixed, True)
        else:
            return StructField(AnimationU8KeyRangeRandom, True)

    curve_types = ListField(EnumField(KeyCurveType, mask=KeyCurveType.Mask), get_param_count)
    padd = ListField(u8(), lambda self: 8 - get_param_count(self), cond=skip_json)
    key_data = UnionField(get_key_data)

################
# Range Values #
################

class AnimationU8Ranges(Structure):
    values = ListField(u8(), lambda self: 2 * get_param_count(self))

##################
# Parsed Formats #
##################

class AnimationU8Target(Structure):
    def has_value(self, _) -> bool:
        return get_key_type(self) == KeyType.Fixed

    def has_range(self, _) -> bool:
        return get_key_type(self) == KeyType.Range

    interpolation = EnumField(KeyCurveType, mask=KeyCurveType.Mask)
    value = u8(cond=has_value)
    range = ListField(u8(), 2, cond=has_range)


class AnimationU8ColorTarget(Structure):
    def has_r_target(self, _) -> bool:
        return check_enabled_target(self, AnimationU8ColorTargets.Red)

    def has_g_target(self, _) -> bool:
        return check_enabled_target(self, AnimationU8ColorTargets.Green)

    def has_b_target(self, _) -> bool:
        return check_enabled_target(self, AnimationU8ColorTargets.Blue)

    r = StructField(AnimationU8Target, cond=has_r_target)
    g = StructField(AnimationU8Target, cond=has_g_target)
    b = StructField(AnimationU8Target, cond=has_b_target)


class AnimationU8OtherTarget(Structure):
    def has_target(self, _) -> bool:
        return check_enabled_target(self, AnimationU8OtherTargets.Main)

    m = StructField(AnimationU8Target, unroll=True, cond=has_target)


class AnimationU8Frame(KeyFrameBase):
    def has_random_seed(self, _) -> bool:
        return self.value_type == KeyType.Random

    def get_target_format(self) -> Field:
        match get_anim_header(self).target:
            case AnimTargetU8.Color1Primary.name | AnimTargetU8.Color2Primary.name | \
                AnimTargetU8.Color1Secondary.name | AnimTargetU8.Color2Secondary.name:
                return StructField(AnimationU8ColorTarget)
            case _:
                return StructField(AnimationU8OtherTarget, unroll=True)

    random_seed = u16(cond=has_random_seed)
    targets = UnionField(get_target_format)


class AnimationU8RandomPoolColorEntry(Structure):
    def has_r_target(self, _) -> bool:
        return check_enabled_target(self, AnimationU8ColorTargets.Red)

    def has_g_target(self, _) -> bool:
        return check_enabled_target(self, AnimationU8ColorTargets.Green)

    def has_b_target(self, _) -> bool:
        return check_enabled_target(self, AnimationU8ColorTargets.Blue)

    r = ListField(u8(), 2, cond=has_r_target)
    g = ListField(u8(), 2, cond=has_g_target)
    b = ListField(u8(), 2, cond=has_b_target)


class AnimationU8RandomPoolOtherEntry(Structure):
    def has_m_target(self, _) -> bool:
        return check_enabled_target(self, AnimationU8OtherTargets.Main)

    m = ListField(u8(), 2, cond=has_m_target)


class AnimationU8RandomPoolEntry(Structure):
    def get_entry_format(self) -> Field:
        match get_anim_header(self).target:
            case AnimTargetU8.Color1Primary.name | AnimTargetU8.Color2Primary.name | \
                AnimTargetU8.Color1Secondary.name | AnimTargetU8.Color2Secondary.name:
                return StructField(AnimationU8RandomPoolColorEntry, unroll=True)
            case _:
                return StructField(AnimationU8RandomPoolOtherEntry, unroll=True)

    entry = UnionField(get_entry_format)

###############
# Main Format #
###############

# TODO finish and beautify format
class AnimationU8(Structure):

    def get_key_count(self) -> int:
        return self.frame_table.entry_count

    def has_range_table(self, is_json: bool) -> bool:
        return not is_json and self.parent.range_table_size != 0

    def get_range_count(self) -> int:
        return self.range_table.entry_count

    def has_random_table(self, is_json: bool) -> bool:
        return not is_json and self.parent.random_table_size != 0

    def get_random_count(self) -> int:
        return self.random_table.entry_count

    frame_table = StructField(AnimDataTable, cond=skip_json)
    frames = ListField(StructField(AnimationU8Key), get_key_count, alignment=4, cond=skip_json)
    key_frames = ListField(StructField(AnimationU8Frame), cond=skip_binary) # Parsed version

    range_table = StructField(AnimDataTable, cond=has_range_table)
    range_values = ListField(StructField(AnimationU8Ranges), get_range_count, cond=has_range_table,
                             alignment=4)

    random_table = StructField(AnimDataTable, cond=has_random_table)
    random_values = ListField(StructField(AnimationU8Ranges), get_random_count, cond=has_random_table,
                            alignment=4)
    random_pool = ListField(StructField(AnimationU8RandomPoolEntry, True), cond=skip_binary)

    def get_targets(self) -> IntFlag:
        match get_anim_header(self).target:
            case AnimTargetU8.Color1Primary.name | AnimTargetU8.Color2Primary.name | \
                AnimTargetU8.Color1Secondary.name | AnimTargetU8.Color2Secondary.name:
                return AnimationU8ColorTargets
            case _:
                return AnimationU8OtherTargets

    def to_json(self) -> dict[str, Any]:

        # Parse each frame
        targets = self.get_targets()
        for frame in self.frames:

            # Copy the basic info
            parsed_frame = AnimationU8Frame(self)
            parsed_frame.frame = frame.frame
            parsed_frame.value_type = frame.value_type

            # Copy the random seed if necessary
            if frame.value_type == KeyType.Random:
                parsed_frame.random_seed = frame.key_data.idx

            # Get the key data type, insert it and create the structure
            key_field: StructField = AnimationU8Frame.targets.type_selector(self)
            parsed_frame._fields_['targets'] = key_field
            key_data: AnimationU8ColorTarget | AnimationU8OtherTarget = key_field.struct_type(self)
            parsed_frame.targets = key_data

            # Parse the enabled targets
            i = 0
            for target in targets:
                if check_enabled_target(frame, target):

                    # Create the target and insert it into the data
                    target_data = AnimationU8Target(parsed_frame)
                    setattr(key_data, target.name[:1].lower(), target_data)

                    # Get the interpolation and value/range
                    target_data.interpolation = frame.curve_types[i]
                    if parsed_frame.value_type == KeyType.Fixed:
                        target_data.value = frame.key_data.values[i]
                    elif parsed_frame.value_type == KeyType.Range:
                        range_idx = frame.key_data.idx
                        range_values: AnimationU8Ranges = self.range_values[range_idx]
                        target_data.range = range_values.values[i : i + 2]

                    # Update the counter
                    i += 1

            # Add the parsed frame to the list
            self.key_frames.append(parsed_frame)

        # Parse the random pool entries
        for entry in self.random_values:

            # Create parsed entry
            pool_entry = AnimationU8RandomPoolEntry(self)

            # Get the pool entry data type, insert it and create the structure
            pool_entry_field: StructField = AnimationU8RandomPoolEntry.entry.type_selector(self)
            pool_entry._fields_['entry'] = pool_entry_field
            pool_entry_data = pool_entry_field.struct_type(pool_entry)
            pool_entry.entry = pool_entry_data

            # Check the enabled targets
            i = 0
            for target in targets:
                if check_enabled_target(frame, target):

                    # Insert the range in the parsed pool entry
                    setattr(pool_entry_data, target.name[:1].lower(), entry.values[i:i+2])
                    i += 2

            # Add the new entry
            self.random_pool.append(pool_entry)

        # Let the parser do the rest
        return super().to_json()
