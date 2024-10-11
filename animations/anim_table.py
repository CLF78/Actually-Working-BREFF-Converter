#!/usr/bin/env python3

# anim_table.py
# Animation table definitions

import struct
from dataclasses import dataclass

from common.common import BaseBinary, fieldex
from animations.anim_base import AnimationBase
from animations.anim_types import *

@dataclass
class AnimationTable(BaseBinary):
    anim_count: int = fieldex('H')
    init_anim_count: int = fieldex('H')
    anim_sizes: list[int] = fieldex(ignore_binary=True)

    @classmethod
    def from_bytes(cls, data: bytes, offset: int = 0, parent = None) -> 'AnimationTable':

        # Parse the two initial fields
        ret: AnimationTable = super().from_bytes(data, offset, parent)
        offset += ret.size(None, 'init_anim_count')

        # Skip the animation pointers
        offset += 4 * ret.anim_count

        # Read the animation lengths
        for _ in range(ret.anim_count):
            ret.anim_sizes.append(struct.unpack_from('>I', data, offset)[0])
            offset += 4

        # Return class
        return ret

    def to_bytes(self) -> bytes:

        # Pack main fields
        data = super().to_bytes()

        # Pack empty anim pointers
        data += struct.pack(f'{4 * self.anim_count}x')

        # Pack anim sizes
        for size in self.anim_sizes:
            data += struct.pack('>I', size)

        # Return the data
        return data

    def size(self, start_field: str = None, end_field: str = None) -> int:

        # Get the fixed size
        size = super().size(start_field, end_field)

        # Add the animation sizes if included
        if end_field is None or end_field == 'anim_sizes':
            size += 8 * self.anim_count

        # Remove the animation pointers if unwanted
        if start_field == 'anim_sizes':
            size -= 4 * self.anim_count

        # Return size
        return size


@dataclass
class Animations(BaseBinary):
    particle_anim_table: AnimationTable = fieldex(ignore_json=True)
    emitter_anim_table: AnimationTable = fieldex(ignore_json=True)
    particle_anims: list[AnimationBase] = fieldex(ignore_binary=True, ignore_json=True)
    emitter_anims: list[AnimationBase] = fieldex(ignore_binary=True, ignore_json=True)
    animations: list[AnimationBase] = fieldex(ignore_binary=True)

    @classmethod
    def from_bytes(cls, data: bytes, offset: int = 0, parent = None) -> 'Animations':
        ret = super().from_bytes(data, offset, parent)

        # Skip to the end of the table
        offset += ret.size(None, 'emitter_anim_table')

        # Parse the individual particle animations
        for size in ret.particle_anim_table.anim_sizes:
            ret.particle_anims.append(AnimationBase.from_bytes(data, offset, ret))
            offset += size

        # Parse the individual emitter animations
        for size in ret.emitter_anim_table.anim_sizes:
            ret.emitter_anims.append(AnimationBase.from_bytes(data, offset, ret))
            offset += size

        # Return data
        return ret

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
                self.emitter_anim_table.anim_sizes.append(anim_size)
                emitter_anims += anim_encoded
                if anim.is_init:
                    self.emitter_anim_table.init_anim_count += 1
            else:
                self.particle_anim_table.anim_count += 1
                self.particle_anims.append(anim)
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
