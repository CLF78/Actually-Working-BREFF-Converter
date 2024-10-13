#!/usr/bin/env python3

# child.py
# Child animation definitions

from enum import Flag, auto
from dataclasses import dataclass

from common.common import BaseBinary, CEnum, fieldex
from animations.tables.name import NameTable
from animations.tables.key import KeyFrameBase, KeyType
from animations.header import AnimationHeader

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
class NormalKeyFrame(KeyFrameBase):
    pad: int = fieldex('7xB', ignore_json=True) # Curve types, not used by child animations
    param: AnimationChildParam = fieldex(unroll_content=True) # The actual data


@dataclass
class RandomKeyFrame(KeyFrameBase):
    rand_idx: int = fieldex('7xH12x') # Used as part of the randomization algorithm


@dataclass
class AnimationChildKeyFrame(BaseBinary):
    @classmethod
    def from_bytes(cls, data: bytes, offset: int = 0, parent = None) -> 'KeyFrameBase':

        # Get the key type
        key_type = KeyType(int.from_bytes(data[offset+2:offset+3]))

        # Create the key frame depending on the type
        if key_type == KeyType.Fixed:
            return NormalKeyFrame.from_bytes(data, offset, parent)
        elif key_type == KeyType.Random:
            return RandomKeyFrame.from_bytes(data, offset, parent)
        else:
            raise ValueError('Invalid key type for Child animation.')

    @classmethod
    def from_json(cls, data: dict, parent = None) -> 'KeyFrameBase':

        # Get the key type
        key_type = KeyType(data['key_type'])

        # Create the key frame depending on the type
        if key_type == KeyType.Fixed:
            return NormalKeyFrame.from_json(data, parent)
        elif key_type == KeyType.Random:
            return RandomKeyFrame.from_json(data, parent)
        else:
            raise ValueError('Invalid key type for Child animation.')


@dataclass
class AnimationChild(AnimationHeader):
    key_frame_count: int = fieldex('H2x', ignore_json=True)
    key_frames: list[AnimationChildKeyFrame] = fieldex(count_field='key_frame_count')
    name_table: NameTable = fieldex(ignore_json=True)
    random_pool_size: int = fieldex('H2x', ignore_binary=True, ignore_json=True)
    random_pool: list[AnimationChildParam] = fieldex(ignore_binary=True, count_field='random_pool_size')

    @classmethod
    def from_bytes(cls, data: bytes, offset: int = 0, parent = None) -> 'AnimationChild':

        # Get the default data
        ret = super().from_bytes(data, offset, parent)
        offset += ret.size()

        # If the random pool is defined, import it
        if ret.random_pool_size:
            offset = ret.field_from_bytes('random_pool_size', data, offset)
            offset = ret.field_from_bytes('random_pool', data, offset)

        # Return data
        return ret

    def to_bytes(self) -> bytes:

        # Calculate key frame count and random pool size
        self.key_frame_count = len(self.key_frames)
        self.random_pool_size = len(self.random_pool)
        self.key_table_size = self.field_size('key_frame_count')

        # Fill the name table
        for frame in self.key_frames:
            if isinstance(frame, NormalKeyFrame):

                # Add the name to the name table
                if frame.param.name not in self.name_table.names:
                    self.name_table.names.append(frame.param.name)

                # Get the name index
                frame.param.name_idx = self.name_table.names.index(frame.param.name)

            # Update table size
            self.key_table_size += frame.size()

        # Find more potential names in the random pool
        for entry in self.random_pool:
            if entry.name not in self.name_table.names:
                self.name_table.names.append(entry.name)
            entry.name_idx = self.name_table.names.index(entry.name)

        # Update the name table sizes
        self.name_table_size = self.name_table.size()

        # Also update the random table size if not empty
        if self.random_pool_size:
            self.random_table_size = self.field_size('random_pool_size') + self.field_size('random_pool')

        # Encode data
        return super().to_bytes()

    def to_json(self) -> dict:
        for frame in self.key_frames:
            if isinstance(frame, NormalKeyFrame):
                frame.param.name = self.name_table.names[frame.param.name_idx].name
        return super().to_json()
