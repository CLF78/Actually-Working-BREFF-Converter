#!/usr/bin/env python3

# u8baked.py
# Particle U8 baked animation definitions

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

def check_enabled_target(structure: Structure, target: IntFlag) -> bool:
    return (get_anim_header(structure).kind_enable & target) != 0

##############
# Key Format #
##############

class AnimationU8BakedKey(Structure):
    values = ListField(u8(), get_param_count)

##################
# Parsed Formats #
##################

class AnimationU8BakedColorFrame(Structure):
    def has_r_target(self, _) -> bool:
        return check_enabled_target(self, AnimationU8ColorTargets.Red)

    def has_g_target(self, _) -> bool:
        return check_enabled_target(self, AnimationU8ColorTargets.Green)

    def has_b_target(self, _) -> bool:
        return check_enabled_target(self, AnimationU8ColorTargets.Blue)

    r = u8(cond=has_r_target)
    g = u8(cond=has_g_target)
    b = u8(cond=has_b_target)


class AnimationU8BakedAlphaFrame(Structure):
    def has_target(self, _) -> bool:
        return check_enabled_target(self, AnimationU8AlphaTargets.Alpha)

    a = u8(cond=has_target)


class AnimationU8BakedFrame(Structure):
    def get_target_format(self) -> Field:
        match get_anim_header(self).target:
            case AnimTargetU8.Color1Primary.name | AnimTargetU8.Color2Primary.name | \
                AnimTargetU8.Color1Secondary.name | AnimTargetU8.Color2Secondary.name:
                return StructField(AnimationU8BakedColorFrame, unroll=True)
            case _:
                return StructField(AnimationU8BakedAlphaFrame, unroll=True)

    targets = UnionField(get_target_format)

###############
# Main Format #
###############

class AnimationU8Baked(Structure):
    def get_key_count(self) -> int:
        return get_anim_header(self).frame_count

    keys = ListField(StructField(AnimationU8BakedKey), get_key_count, alignment=4, cond=skip_json)
    frames = ListField(StructField(AnimationU8BakedFrame, unroll=True), cond=skip_binary) # Parsed version

    def get_targets(self) -> IntFlag:
        match get_anim_header(self).target:
            case AnimTargetU8.Color1Primary.name | AnimTargetU8.Color2Primary.name | \
                AnimTargetU8.Color1Secondary.name | AnimTargetU8.Color2Secondary.name:
                return AnimationU8ColorTargets
            case _:
                return AnimationU8AlphaTargets

    def to_json(self) -> dict[str, Any]:

        # Parse each frame
        targets = self.get_targets()
        for key in self.keys:

            # Create the target data
            parsed_frame = AnimationU8BakedFrame(self)
            key_data = AnimationU8BakedFrame.targets.detect_field(parsed_frame).struct_type(parsed_frame)
            parsed_frame.targets = key_data

            # Parse the enabled targets
            i = 0
            for target in targets:
                if check_enabled_target(self, target):
                    setattr(key_data, target.name[:1].lower(), key.values[i])
                    i += 1

            # Add the parsed frame to the list
            self.frames.append(parsed_frame)

        # Let the parser do the rest
        return super().to_json()
