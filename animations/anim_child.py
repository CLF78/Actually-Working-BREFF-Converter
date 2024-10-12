#!/usr/bin/env python3

# anim_child.py
# Child animation definitions

from enum import Flag, auto
from dataclasses import dataclass

from common.common import BaseBinary, CEnum, fieldex
from animations.anim_tables import NameTable

class ChildType(CEnum):
    Particle = auto()
    Emitter = auto()


class ChildFlag(Flag):
    FollowEmitter   = 1 << 0 # Unused
    InheritRotation = 1 << 1


class AlphaInheritanceFlag(Flag):
    PrimaryAlpha          = 1 << 0
    SecondaryAlpha        = 1 << 1
    AlphaFlickAndModifier = 1 << 2


@dataclass
class AnimationChildFrame(BaseBinary):
    frame: int = fieldex('H')
    name: str = fieldex(ignore_binary=True)

    # TODO figure out what the fuck these mean, although they seem to always be 0...
    flag: int = fieldex('Bx')
    curve_types: int = fieldex('Q')

    # These may not be correct if randomized, but i'm not certain
    speed: int = fieldex('h') # Used for all axes
    scale: int = fieldex('B') # Used for all axes
    alpha: int = fieldex('B') # Used for both primary and secondary
    color: int = fieldex('B') # Used for all color channels, both primary and secondary
    render_priority: int = fieldex('B', default=128)
    child_type: ChildType = fieldex('B')
    child_flags: ChildFlag = fieldex('B')
    alpha_primary_sources: AlphaInheritanceFlag = fieldex('B')
    alpha_secondary_sources: AlphaInheritanceFlag = fieldex('B')
    name_idx: int = fieldex('H', ignore_json=True)


@dataclass
class AnimationChild(BaseBinary):
    key_frame_count: int = fieldex('H2x', ignore_json=True)
    key_frames: list[AnimationChildFrame] = fieldex(count_field='key_frame_count')
    name_table: NameTable = fieldex(ignore_json=True)

    def to_bytes(self) -> bytes:

        # Calculate frame count
        self.key_frame_count = len(self.key_frames)

        # Fill the name table
        for frame in self.key_frames:
            if frame.name not in self.name_table.names:
                self.name_table.names.append(frame.name)
            frame.name_idx = self.name_table.names.index(frame.name)

        # Update the table sizes
        parent = self.parent
        parent.key_table_size = self.size(None, 'name_table')
        parent.range_table_size = 0
        parent.random_table_size = 0
        parent.name_table_size = self.name_table.size()
        parent.info_table_size = 0

        # Encode data
        return super().to_bytes()

    def to_json(self) -> dict:
        for frame in self.key_frames:
            frame.name = self.name_table.names[frame.name_idx].name
        return super().to_json()
