#!/usr/bin/env python3

# rotate.py
# Particle rotation animation definitions

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

###############
# Key Formats #
###############

class AnimationRotateKeyFixed(Structure):
    values = ListField(f32(), get_param_count)

class AnimationRotateKeyRangeRandom(Structure):
    def get_padding(self) -> int:
        param_size = get_anim_header(self).get_param_count() * 4
        return 0xC + param_size - 0xE

    idx = u16()
    padd = ListField(u8(), get_padding, cond=skip_json)


class AnimationRotateKey(KeyFrameBase):
    def get_key_data(self) -> Field:
        if self.value_type == KeyType.Fixed:
            return StructField(AnimationRotateKeyFixed, True)
        else:
            return StructField(AnimationRotateKeyRangeRandom, True)

    curve_types = ListField(EnumField(KeyCurveType, mask=KeyCurveType.Mask), 8)
    key_data = UnionField(get_key_data)

################
# Range Values #
################

class AnimationRotateRanges(Structure):
    values = ListField(f32(), lambda self: 2 * get_param_count(self))
    random_rotation_direction = boolean('?3x')

##################
# Parsed Formats #
##################

class AnimationRotateTarget(Structure):
    def has_value(self, _) -> bool:
        return get_key_type(self) == KeyType.Fixed

    def has_range(self, _) -> bool:
        return get_key_type(self) == KeyType.Range

    interpolation = EnumField(KeyCurveType, mask=KeyCurveType.Mask)
    value = f32(cond=has_value)
    range = ListField(f32(), 2, cond=has_range)


class AnimationF32Frame(KeyFrameBase):
    def has_random_seed(self, _) -> bool:
        return self.value_type == KeyType.Random

    def has_random_rotation_dir(self, _) -> bool:
        return self.value_type == KeyType.Range

    def has_x_target(self, _) -> bool:
        return check_enabled_target(self, AnimationF32Targets.X)

    def has_y_target(self, _) -> bool:
        return check_enabled_target(self, AnimationF32Targets.Y)

    def has_z_target(self, _) -> bool:
        return check_enabled_target(self, AnimationF32Targets.Z)

    random_seed = u16(cond=has_random_seed)
    random_rotation_direction = boolean('?3x', cond=has_random_rotation_dir)
    x = StructField(AnimationRotateTarget, cond=has_x_target)
    y = StructField(AnimationRotateTarget, cond=has_y_target)
    z = StructField(AnimationRotateTarget, cond=has_z_target)


class AnimationRotateRandomPoolEntry(Structure):
    def has_random_rotation_dir(self, _) -> bool:
        return self.value_type == KeyType.Range

    def has_x_target(self, _) -> bool:
        return check_enabled_target(self, AnimationF32Targets.X)

    def has_y_target(self, _) -> bool:
        return check_enabled_target(self, AnimationF32Targets.Y)

    def has_z_target(self, _) -> bool:
        return check_enabled_target(self, AnimationF32Targets.Z)

    random_rotation_direction = boolean('?3x', cond=has_random_rotation_dir)
    x = StructField(AnimationRotateTarget, cond=has_x_target)
    y = StructField(AnimationRotateTarget, cond=has_y_target)
    z = StructField(AnimationRotateTarget, cond=has_z_target)

###############
# Main Format #
###############

class AnimationRotate(Structure):

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
    frames = ListField(StructField(AnimationRotateKey), get_key_count, cond=skip_json)
    key_frames = ListField(StructField(AnimationF32Frame), cond=skip_binary) # Parsed version

    range_table = StructField(AnimDataTable, cond=has_range_table)
    range_values = ListField(StructField(AnimationRotateRanges), get_range_count, cond=has_range_table)

    random_table = StructField(AnimDataTable, cond=has_random_table)
    random_values = ListField(StructField(AnimationRotateRanges), get_random_count, cond=has_random_table)
    random_pool = ListField(StructField(AnimationRotateRandomPoolEntry, True), cond=skip_binary) # Parsed version

    def to_json(self) -> dict[str, Any]:

        # Parse each frame
        for frame in self.frames:

            # Copy the basic info
            parsed_frame = AnimationF32Frame(self)
            parsed_frame.frame = frame.frame
            parsed_frame.value_type = frame.value_type

            # Copy the random seed if necessary
            if frame.value_type == KeyType.Random:
                parsed_frame.random_seed = frame.key_data.idx
            elif frame.value_type == KeyType.Range:
                range_idx = frame.key_data.idx
                parsed_frame.random_rotation_direction = self.range_values[range_idx].random_rotation_direction

            # Parse the enabled targets
            i = 0
            for target in AnimationF32Targets:
                if check_enabled_target(frame, target):

                    # Create the target and insert it into the data
                    target_data = AnimationRotateTarget(parsed_frame)
                    setattr(parsed_frame, target.name.lower(), target_data)

                    # Get the interpolation and value/range
                    target_data.interpolation = frame.curve_types[target.value.bit_length() - 1]
                    if parsed_frame.value_type == KeyType.Fixed:
                        target_data.value = frame.key_data.values[i]
                    elif parsed_frame.value_type == KeyType.Range:
                        range_idx = frame.key_data.idx
                        range_values: AnimationRotateRanges = self.range_values[range_idx]
                        target_data.range = range_values.values[i*2 : i*2 + 2]

                    # Update the counter
                    i += 1

            # Add the parsed frame to the list
            self.key_frames.append(parsed_frame)

        # Parse the random pool entries
        for entry in self.random_values:

            # Create parsed entry
            pool_entry = AnimationRotateRandomPoolEntry(self)

            # Check the enabled targets
            i = 0
            for target in AnimationF32Targets:
                if check_enabled_target(self, target):

                    # Insert the range in the parsed pool entry
                    setattr(pool_entry, target.name.lower(), entry.values[i:i+2])
                    i += 2

            # Add the new entry
            self.random_pool.append(pool_entry)

        # Let the parser do the rest
        return super().to_json()
