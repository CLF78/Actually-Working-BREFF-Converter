#!/usr/bin/env python3

# f32baked.py
# Particle F32 baked animation definitions

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

class AnimationF32BakedKey(Structure):
    values = ListField(f32(), get_param_count)

##################
# Parsed Formats #
##################

class AnimationF32BakedFrame(Structure):
    def has_x_target(self, _) -> bool:
        return check_enabled_target(self, AnimationF32Targets.X)

    def has_y_target(self, _) -> bool:
        return check_enabled_target(self, AnimationF32Targets.Y)

    def has_z_target(self, _) -> bool:
        return check_enabled_target(self, AnimationF32Targets.Z)

    x = u8(cond=has_x_target)
    y = u8(cond=has_y_target)
    z = u8(cond=has_z_target)

###############
# Main Format #
###############

class AnimationF32Baked(Structure):
    def get_key_count(self) -> int:
        return get_anim_header(self).frame_count

    keys = ListField(StructField(AnimationF32BakedKey), get_key_count, cond=skip_json)
    frames = ListField(StructField(AnimationF32BakedFrame, unroll=True), cond=skip_binary) # Parsed version

    def to_json(self) -> dict[str, Any]:

        # Parse each frame
        for key in self.keys:

            # Create the target data
            parsed_frame = AnimationF32BakedFrame(self)

            # Parse the enabled targets
            i = 0
            for target in AnimationF32Targets:
                if check_enabled_target(self, target):
                    setattr(parsed_frame, target.name.lower(), key.values[i])
                    i += 1

            # Add the parsed frame to the list
            self.frames.append(parsed_frame)

        # Let the parser do the rest
        return super().to_json()
