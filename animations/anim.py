#!/usr/bin/env python3

# anim.py
# Animation definitions

from common.field import *
from animations.header import AnimationHeader
from animations.flags import AnimTargetEmitterF32

class AnimationTable(Structure):
    anim_count = u16(default=0)
    init_anim_count = u16(default=0)
    anim_ptrs = ListField(u32(), anim_count)
    anim_sizes = ListField(u32(), anim_count)

    def encode(self) -> None:
        self.anim_ptrs = [0] * self.anim_count
        super().encode()


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

    def decode(self) -> None:

        # Mark animations that need to run on frame 0 only
        for i, anim in enumerate(self.particle_anims):
            anim.is_init = i < self.particle_anim_table.init_anim_count

        # Mark animations that need to run on frame 0 only
        for i, anim in enumerate(self.emitter_anims):
            anim.is_init = i < self.emitter_anim_table.init_anim_count

        # Merge animation lists and decode result
        self.animations = self.particle_anims + self.emitter_anims
        super().decode()

    def encode(self) -> None:

        # Create tables
        self.particle_anim_table = AnimationTable(self)
        self.emitter_anim_table = AnimationTable(self)

        # Encode animations and distribute them between the particle and emitter tables
        for anim in self.animations:
            anim.encode()
            if anim.target in AnimTargetEmitterF32.__members__.keys():
                self.emitter_anims.append(anim)
            else:
                self.particle_anims.append(anim)

        # Sort the tables to ensure init animations are placed first
        self.particle_anims.sort(key=lambda x: x.is_init, reverse=True)
        self.emitter_anims.sort(key=lambda x: x.is_init, reverse=True)

        # Update particle animation counts
        for anim in self.particle_anims:
            self.particle_anim_table.anim_count += 1
            self.particle_anim_table.anim_sizes.append(anim.size())
            if anim.is_init:
                self.particle_anim_table.init_anim_count += 1

        # Update emitter animation counts
        for anim in self.emitter_anims:
            self.emitter_anim_table.anim_count += 1
            self.emitter_anim_table.anim_sizes.append(anim.size())
            if anim.is_init:
                self.emitter_anim_table.init_anim_count += 1

        # Encode the tables
        self.particle_anim_table.encode()
        self.emitter_anim_table.encode()
