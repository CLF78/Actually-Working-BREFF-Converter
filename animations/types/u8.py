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

def get_param_count(structure: Structure) -> int:
    from animations.header import AnimationHeader
    return structure.get_parent(AnimationHeader).get_param_count()


def get_key_type(structure: Structure) -> KeyType:
    return structure.get_parent(AnimationU8BeautifiedFrame).value_type


def get_key_data(key: 'AnimationU8Key') -> Field:
    if key.value_type == KeyType.Fixed:
        return StructField(AnimationU8KeyFixed, True)
    else:
        return StructField(AnimationU8KeyRangeRandom, True)


def get_beautified_key_data(key: 'AnimationU8Key') -> Field:
    from animations.header import AnimationHeader
    target = key.get_parent(AnimationHeader).target

    match target:
        case AnimTargetU8.Color1Primary.name | AnimTargetU8.Color2Primary.name | \
             AnimTargetU8.Color1Secondary.name | AnimTargetU8.Color2Secondary.name:
            return StructField(AnimationU8BeautifiedColorTarget)
        case _:
            return StructField(AnimationU8BeautifiedOtherTarget, unroll=True)


def get_enabled_target(structure: Structure, target: IntFlag) -> bool:
    from animations.header import AnimationHeader
    return (structure.get_parent(AnimationHeader).kind_enable & target) != 0


def get_beautified_target(key: 'AnimationU8Key') -> IntFlag:
    from animations.header import AnimationHeader
    target = key.get_parent(AnimationHeader).target

    match target:
        case AnimTargetU8.Color1Primary.name | AnimTargetU8.Color2Primary.name | \
             AnimTargetU8.Color1Secondary.name | AnimTargetU8.Color2Secondary.name:
            return AnimationU8TargetColor
        case _:
            return AnimationU8TargetOther

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
    curve_types = ListField(EnumField(KeyCurveType, mask=KeyCurveType.Mask), get_param_count)
    padd = ListField(u8(), lambda x: 8 - get_param_count(x), skip_json=True)
    key_data = UnionField(get_key_data)


################
# Range Values #
################

class AnimationU8RangeValue(Structure):
    values = ListField(u8(), lambda x: 2 * get_param_count(x))


##################
# Parsed Formats #
##################


class AnimationU8BeautifiedTarget(Structure):
    interp_type = EnumField(KeyCurveType, mask=KeyCurveType.Mask)
    value = u8(cond=lambda x: get_key_type(x) == KeyType.Fixed)
    range = ListField(u8(), 2, cond=lambda x: get_key_type(x) == KeyType.Range)


class AnimationU8BeautifiedColorTarget(Structure):
    r = StructField(AnimationU8BeautifiedTarget, cond=lambda x: get_enabled_target(x, AnimationU8TargetColor.Red))
    g = StructField(AnimationU8BeautifiedTarget, cond=lambda x: get_enabled_target(x, AnimationU8TargetColor.Green))
    b = StructField(AnimationU8BeautifiedTarget, cond=lambda x: get_enabled_target(x, AnimationU8TargetColor.Blue))


class AnimationU8BeautifiedOtherTarget(Structure):
    m = StructField(AnimationU8BeautifiedTarget, unroll=True, cond=lambda x: get_enabled_target(x, AnimationU8TargetOther.Main))


class AnimationU8BeautifiedFrame(KeyFrameBase):
    random_seed = u16(cond=lambda x: get_key_type(x) == KeyType.Random)
    targets = UnionField(get_beautified_key_data)


###############
# Main Format #
###############

# TODO finish and beautify format
class AnimationU8(Structure):
    frame_table = StructField(AnimDataTable, skip_json=True)
    frames = ListField(StructField(AnimationU8Key), lambda x: x.frame_table.entry_count,
                       alignment=4, skip_json=True)
    key_frames = ListField(StructField(AnimationU8BeautifiedFrame), skip_binary=True) # Parsed version

    range_table = StructField(AnimDataTable, cond=lambda x: x.parent.range_table_size != 0, skip_json=True)
    range_values = ListField(StructField(AnimationU8RangeValue), lambda x: x.range_table.entry_count,
                             cond=lambda x: x.parent.range_table_size != 0, alignment=4, skip_json=True)

    random_table = StructField(AnimDataTable, cond=lambda x: x.parent.random_table_size != 0, skip_json=True)
    random_pool = ListField(StructField(AnimationU8RangeValue), lambda x: x.random_table.entry_count,
                            cond=lambda x: x.parent.random_table_size != 0, alignment=4, skip_json=True)

    def to_json(self) -> dict[str, Any]:

        # Parse each frame
        self.key_frames.clear()
        for frame in self.frames:
            frame: AnimationU8Key = frame[1]

            # Get the basic info
            parsed_frame = AnimationU8BeautifiedFrame(self)
            parsed_frame.frame = frame.frame
            parsed_frame.value_type = frame.value_type

            # Add the random seed if necessary
            if frame.value_type == KeyType.Random:
                parsed_frame.random_seed = frame.key_data.idx

            # Get the key data type, set it in the union and create the structure
            key_field: StructField = AnimationU8BeautifiedFrame.targets.type_selector(self)
            parsed_frame._fields_['targets'] = key_field
            key_data: AnimationU8BeautifiedColorTarget | AnimationU8BeautifiedOtherTarget = key_field.struct_type(self)
            parsed_frame.targets = key_data

            # Get the associated targets and skip disabled ones
            targets = get_beautified_target(frame)
            i = 0
            for target in targets:
                if get_enabled_target(frame, target):

                    # Create the target and insert it into the data
                    target_data = AnimationU8BeautifiedTarget(parsed_frame)
                    setattr(key_data, target.name[:1].lower(), target_data)

                    # Get the interpolation and value/range
                    target_data.interp_type = frame.curve_types[i][1]
                    if parsed_frame.value_type == KeyType.Fixed:
                        target_data.value = frame.key_data.values[i][1]
                    elif parsed_frame.value_type == KeyType.Range:
                        range_idx = frame.key_data.idx
                        range_values: AnimationU8RangeValue = self.range_values[range_idx][1]
                        target_data.range = range_values.values[i : i + 2]

                    # Update the counter
                    i += 1

            # Add the parsed frame to the list
            self.key_frames.append((AnimationU8.key_frames.item_field, parsed_frame))

        # Let the parser do the rest
        return super().to_json()
