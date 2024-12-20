#!/usr/bin/env python3

# u8baked.py
# Particle U8 baked animation definitions

from typing import Any
from common.common import pascal_to_snake
from common.field import *
from animations.common import *
from animations.tables import *

##############
# Key Format #
##############

class AnimationU8BakedKey(Structure):
    values = ListField(u8(), get_sub_target_count)

##################
# Parsed Formats #
##################

class AnimationU8BakedFrame(Structure):
    def has_r_target(self, _) -> bool:
        return self.r is not None

    def has_g_target(self, _) -> bool:
        return self.g is not None

    def has_b_target(self, _) -> bool:
        return self.b is not None

    r = u8(cond=has_r_target)
    g = u8(cond=has_g_target)
    b = u8(cond=has_b_target)
    t = u8(cond=has_single_target)

###############
# Main Format #
###############

class AnimationU8Baked(Structure):
    def get_key_count(self) -> int:
        return get_anim_header(self).frame_count

    keys = ListField(StructField(AnimationU8BakedKey), get_key_count, alignment=4, cond=skip_json)
    frames = ListField(StructField(AnimationU8BakedFrame, unroll=True), cond=skip_binary) # Parsed version

    def to_json(self) -> dict[str, Any]:

        # Parse each frame
        sub_targets = get_anim_header(self).sub_targets
        for key in self.keys:

            # Create the target data
            parsed_frame = AnimationU8BakedFrame(self)
            for i, target_name, _ in get_enabled_targets(sub_targets):
                setattr(parsed_frame, pascal_to_snake(target_name), key.values[i])

            # Add the parsed frame to the list
            self.frames.append(parsed_frame)

        # Let the parser do the rest
        return super().to_json()

    def to_bytes(self) -> bytes:

        # Get the enabled targets
        sub_targets = get_anim_header(self).sub_targets

        # Parse each frame
        for frame in self.frames:

            # Parse the enabled targets
            key = AnimationU8BakedKey(self)
            for target in sub_targets:
                value = getattr(frame, pascal_to_snake(target.name))
                key.values.append(value)

            # Add the parsed frame to the list
            self.keys.append(key)

        # Calculate key table size and encode the result
        get_anim_header(self).key_table_size = self.size()
        return super().to_bytes()
