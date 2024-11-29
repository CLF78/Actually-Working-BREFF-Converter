#!/usr/bin/env python3

# anim.py
# Animation definitions

from common.field import *
from animations.header import AnimationHeader

class AnimationTable(Structure):
    anim_count = u16()
    init_anim_count = u16()
    anim_ptrs = ListField(u32(), lambda x: x.anim_count)
    anim_sizes = ListField(u32(), lambda x: x.anim_count)


class Animations(Structure):
    particle_anim_table = StructField(AnimationTable, skip_json=True)
    emitter_anim_table = StructField(AnimationTable, skip_json=True)
    particle_anims = ListField(StructField(AnimationHeader), lambda x: x.particle_anim_table.anim_count, skip_json=True)
    emitter_anims = ListField(StructField(AnimationHeader), lambda x: x.emitter_anim_table.anim_count, skip_json=True)
    animations = ListField(StructField(AnimationHeader), skip_binary=True)

    # TODO write this method
    def to_bytes(self) -> bytes:
        return super().to_bytes()

    def to_json(self) -> dict:

        # Mark animations that need to run on frame 0 only
        for i in range(self.particle_anim_table.init_anim_count):
            self.particle_anims[i][1].is_init = True

        # Mark animations that need to run on frame 0 only
        for i in range(self.emitter_anim_table.init_anim_count):
            self.emitter_anims[i][1].is_init = True

        # Merge animation lists
        self.animations = self.particle_anims + self.emitter_anims

        # Serialize data
        return super().to_json()
