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

class AnimationU8TargetColor(IntFlag):
    Red   = 1 << 0
    Green = 1 << 1
    Blue  = 1 << 2

class AnimationU8TargetOther(IntFlag):
    Main = 1 << 0

###############
# Key Formats #
###############

class AnimationU8KeyFixed(Structure):
    values = ListField(u8(), get_param_count, alignment=2)

class AnimationU8KeyRangeRandom(Structure):
    idx = u16()

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

class AnimationU8RangeValue(Structure):
    values = ListField(u8(), lambda self: 2 * get_param_count(self))

##################
# Parsed Formats #
##################

class AnimationU8BeautifiedTarget(Structure):
    def has_value(self, _) -> bool:
        return get_key_type(self) == KeyType.Fixed

    def has_range(self, _) -> bool:
        return get_key_type(self) == KeyType.Range

    interp_type = EnumField(KeyCurveType, mask=KeyCurveType.Mask)
    value = u8(cond=has_value)
    range = ListField(u8(), 2, cond=has_range)


class AnimationU8BeautifiedColorTarget(Structure):
    def has_r_target(self, _) -> bool:
        return check_enabled_target(self, AnimationU8TargetColor.Red)

    def has_g_target(self, _) -> bool:
        return check_enabled_target(self, AnimationU8TargetColor.Green)

    def has_b_target(self, _) -> bool:
        return check_enabled_target(self, AnimationU8TargetColor.Blue)

    r = StructField(AnimationU8BeautifiedTarget, cond=has_r_target)
    g = StructField(AnimationU8BeautifiedTarget, cond=has_g_target)
    b = StructField(AnimationU8BeautifiedTarget, cond=has_b_target)


class AnimationU8BeautifiedOtherTarget(Structure):
    def has_target(self, _) -> bool:
        return check_enabled_target(self, AnimationU8TargetOther.Main)

    m = StructField(AnimationU8BeautifiedTarget, unroll=True, cond=has_target)


class AnimationU8BeautifiedFrame(KeyFrameBase):
    def has_random_seed(self, _) -> bool:
        return self.value_type == KeyType.Random

    def get_target_format(self) -> Field:
        match get_anim_header(self).target:
            case AnimTargetU8.Color1Primary.name | AnimTargetU8.Color2Primary.name | \
                AnimTargetU8.Color1Secondary.name | AnimTargetU8.Color2Secondary.name:
                return StructField(AnimationU8BeautifiedColorTarget)
            case _:
                return StructField(AnimationU8BeautifiedOtherTarget, unroll=True)

    random_seed = u16(cond=has_random_seed)
    targets = UnionField(get_target_format)

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
        return self.parent.random_table_size != 0

    def get_random_count(self) -> int:
        return self.random_table.entry_count

    frame_table = StructField(AnimDataTable, cond=skip_json)
    frames = ListField(StructField(AnimationU8Key), get_key_count, alignment=4, cond=skip_json)
    key_frames = ListField(StructField(AnimationU8BeautifiedFrame), cond=skip_binary) # Parsed version

    range_table = StructField(AnimDataTable, cond=has_range_table)
    range_values = ListField(StructField(AnimationU8RangeValue), get_range_count, cond=has_range_table,
                             alignment=4)

    random_table = StructField(AnimDataTable, cond=has_random_table)
    random_pool = ListField(StructField(AnimationU8RangeValue), get_random_count, cond=has_random_table,
                            alignment=4)

    def get_targets(self) -> IntFlag:
        match get_anim_header(self).target:
            case AnimTargetU8.Color1Primary.name | AnimTargetU8.Color2Primary.name | \
                AnimTargetU8.Color1Secondary.name | AnimTargetU8.Color2Secondary.name:
                return AnimationU8TargetColor
            case _:
                return AnimationU8TargetOther

    def to_json(self) -> dict[str, Any]:

        # Parse each frame
        targets = self.get_targets()
        for frame in self.frames:

            # Copy the basic info
            parsed_frame = AnimationU8BeautifiedFrame(self)
            parsed_frame.frame = frame.frame
            parsed_frame.value_type = frame.value_type

            # Copy the random seed if necessary
            if frame.value_type == KeyType.Random:
                parsed_frame.random_seed = frame.key_data.idx

            # Get the key data type, insert it and create the structure
            key_field: StructField = AnimationU8BeautifiedFrame.targets.type_selector(self)
            parsed_frame._fields_['targets'] = key_field
            key_data: AnimationU8BeautifiedColorTarget | AnimationU8BeautifiedOtherTarget = key_field.struct_type(self)
            parsed_frame.targets = key_data

            # Parse the enabled targets
            i = 0
            for target in targets:
                if check_enabled_target(frame, target):

                    # Create the target and insert it into the data
                    target_data = AnimationU8BeautifiedTarget(parsed_frame)
                    setattr(key_data, target.name[:1].lower(), target_data)

                    # Get the interpolation and value/range
                    target_data.interp_type = frame.curve_types[i]
                    if parsed_frame.value_type == KeyType.Fixed:
                        target_data.value = frame.key_data.values[i]
                    elif parsed_frame.value_type == KeyType.Range:
                        range_idx = frame.key_data.idx
                        range_values: AnimationU8RangeValue = self.range_values[range_idx]
                        target_data.range = range_values.values[i : i + 2]

                    # Update the counter
                    i += 1

            # Add the parsed frame to the list
            self.key_frames.append(parsed_frame)

        # Let the parser do the rest
        return super().to_json()
