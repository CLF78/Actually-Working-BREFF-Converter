#!/usr/bin/env python3

# anim_child.py
# Child animation definitions

import struct
from enum import Flag, auto
from dataclasses import dataclass

from common.common import BaseBinary, CEnum, fieldex
from animations.tables.name_table import NameTable
from animations.tables.key_table import KeyFrameBase, KeyType

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
class AnimationChildParam(BaseBinary):
    name: str = fieldex(ignore_binary=True)
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
class NormalKeyFrame(BaseBinary):
    pad: int = fieldex('7xB', ignore_json=True)
    param: AnimationChildParam = fieldex(unroll_content=True)


@dataclass
class RandomKeyFrame(BaseBinary):
    rand_idx: int = fieldex('7xH12x')


@dataclass
class AnimationChild(BaseBinary):
    key_frame_count: int = fieldex('H2x', ignore_json=True)
    key_frames: list[KeyFrameBase] = fieldex(ignore_binary=True)
    name_table: NameTable = fieldex(ignore_binary=True, ignore_json=True)
    random_pool_size: int = fieldex('H2x', ignore_json=True, ignore_binary=True)
    random_pool: list[AnimationChildParam] = fieldex(ignore_binary=True)

    @classmethod
    def from_bytes(cls, data: bytes, offset: int = 0, parent = None) -> 'AnimationChild':

        # Get the frame count
        ret = super().from_bytes(data, offset, parent)

        # Parse the key table
        key_offset = offset + ret.size()
        for _ in range(ret.key_frame_count):

            # Build the key base
            key = KeyFrameBase.from_bytes(data, key_offset, ret)
            key_offset += key.size()

            # Create the key frame depending on the type
            if key.value_type == KeyType.Fixed:
                param = NormalKeyFrame.from_bytes(data, key_offset, key)
            elif key.value_type == KeyType.Random:
                param = RandomKeyFrame.from_bytes(data, key_offset, key)
            else:
                raise ValueError('Invalid key type for Child animation.')

            # Add key to list and update offset
            key.param = param
            ret.key_frames.append(key)
            key_offset += param.size()

        # Parse the name table
        name_offset = offset + parent.key_table_size + parent.random_table_size
        ret.name_table = NameTable.from_bytes(data, name_offset, ret)

        # Parse the random table if present
        if parent.random_table_size:

            # Get the random pool size
            random_offset = offset + parent.key_table_size
            ret.random_pool_size = struct.unpack_from('>H2x', data, random_offset)

            # Parse the entries in the pool
            for _ in range(ret.random_pool_size):
                param = AnimationChildParam.from_bytes(data, random_offset, ret)
                ret.random_pool.append(param)
                random_offset += param.size()

        # Return result
        return ret

    def to_bytes(self) -> bytes:

        # Calculate key frame count and random pool size
        self.key_frame_count = len(self.key_frames)
        self.random_pool_size = len(self.random_pool)
        self.parent.key_table_size = 4

        # Fill the name table
        for frame in self.key_frames:
            if frame.value_type == KeyType.Fixed:

                # Add the name to the name table
                if frame.param.param.name not in self.name_table.names:
                    self.name_table.names.append(frame.param.param.name)

                # Get the name index
                frame.param.param.name_idx = self.name_table.names.index(frame.name)

            # Update table size
            parent.key_table_size += frame.size()

        # Find more potential names in the random pool
        for entry in self.random_pool:
            if entry.name not in self.name_table.names:
                self.name_table.names.append(entry.name)
            entry.name_idx = self.name_table.names.index(entry.name)

        # Update the table sizes
        parent = self.parent
        parent.range_table_size = 0
        parent.random_table_size = 4 + 12 * self.random_pool_size if self.random_pool else 0
        parent.name_table_size = self.name_table.size()
        parent.info_table_size = 0

        # Encode data
        return super().to_bytes()

    def to_json(self) -> dict:
        for frame in self.key_frames:
            if frame.value_type == KeyType.Fixed:
                frame.param.param.name = self.name_table.names[frame.param.param.name_idx].name
        return super().to_json()
