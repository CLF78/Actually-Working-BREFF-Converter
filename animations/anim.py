#!/usr/bin/env python3

# anim.py
# Animation definition

from dataclasses import dataclass

from common.common import BaseBinary, fieldex
from animations.anim_header import AnimationHeader
from animations.anim_flags import *
from animations.anim_tables import AnimationTable

@dataclass
class Animations(BaseBinary):
    particle_anim_table: AnimationTable = fieldex(ignore_json=True)
    emitter_anim_table: AnimationTable = fieldex(ignore_json=True)
    particle_anims: list[AnimationHeader] = fieldex(ignore_json=True, count_field='particle_anim_table.anim_count')
    emitter_anims: list[AnimationHeader] = fieldex(ignore_json=True, count_field='emitter_anim_table.anim_count')
    animations: list[AnimationHeader] = fieldex(ignore_binary=True)

    def to_bytes(self) -> bytes:

        # Sort animations by their is_init attribute to ensure initial anims are first
        self.animations.sort(key=lambda x: x.is_init, reverse=True)

        # Initialize loop
        particle_anims = b''
        emitter_anims = b''

        # Encode the animations themselves
        for anim in self.animations:
            anim_size = anim.size()
            anim_encoded = anim.to_bytes()

            # Distribute animations depending on the curve type
            if anim.curve_type == AnimType.EmitterF32:
                self.emitter_anim_table.anim_count += 1
                self.emitter_anims.append(anim)
                self.emitter_anim_table.anim_ptrs.append(0)
                self.emitter_anim_table.anim_sizes.append(anim_size)
                emitter_anims += anim_encoded
                if anim.is_init:
                    self.emitter_anim_table.init_anim_count += 1
            else:
                self.particle_anim_table.anim_count += 1
                self.particle_anims.append(anim)
                self.particle_anim_table.anim_ptrs.append(0)
                self.particle_anim_table.anim_sizes.append(anim_size)
                particle_anims += anim_encoded
                if anim.is_init:
                    self.particle_anim_table.init_anim_count += 1

        # Return encoded data
        return super().to_bytes() + particle_anims + emitter_anims

    def to_json(self) -> dict:

        # Mark animations that need to run on frame 0 only
        for i in range(self.particle_anim_table.init_anim_count):
            self.particle_anims[i].is_init = True

        # Mark animations that need to run on frame 0 only
        for i in range(self.emitter_anim_table.init_anim_count):
            self.emitter_anims[i].is_init = True

        # Merge animation lists
        self.animations = self.particle_anims + self.emitter_anims

        # Serialize data
        return super().to_json()
