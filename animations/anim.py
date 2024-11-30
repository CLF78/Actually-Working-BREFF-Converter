#!/usr/bin/env python3

# anim.py
# Animation definitions

from common.field import *
from animations.header import AnimationHeader

class AnimationTable(Structure):
    anim_count = u16()
    init_anim_count = u16()
    anim_ptrs = ListField(u32(), anim_count)
    anim_sizes = ListField(u32(), anim_count)


class Animations(Structure):
    def get_particle_anim_count(self) -> int:
        return self.particle_anim_table.anim_count

    def get_emitter_anim_count(self) -> int:
        return self.emitter_anim_table.anim_count

    particle_anim_table = StructField(AnimationTable, cond=skip_json)
    emitter_anim_table = StructField(AnimationTable, cond=skip_json)
    particle_anims = ListField(StructField(AnimationHeader), get_particle_anim_count, cond=skip_json)
    emitter_anims = ListField(StructField(AnimationHeader), get_emitter_anim_count, cond=skip_json)
    animations = ListField(StructField(AnimationHeader), cond=skip_binary)

    # TODO write this method
    def to_bytes(self) -> bytes:
        return super().to_bytes()

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
