#!/usr/bin/env python3

# tex.py
# Particle texture animation definitions

from enum import IntFlag
from typing import Any
from common.field import *
from common.gx import GXTexWrapMode
from animations.common import *
from animations.tables import *
from particle.texture import ReverseMode

class FlipRandom(IntFlag):
    FlipHorizontal = 1 << 0
    FlipVertical = 1 << 1


class AnimationTexParam(Structure):

    # Parsed fields
    texture_name = string(cond=skip_binary)
    wrapS = EnumField(GXTexWrapMode, cond=skip_binary)
    wrapT = EnumField(GXTexWrapMode, cond=skip_binary)

    # Actual fields
    wrap = u8(cond=skip_json)
    reverse_mode = EnumField(ReverseMode)
    name_idx = u16(cond=skip_json)

    def to_json(self) -> dict[str, Any]:
        self.texture_name = self.get_parent(AnimationTex).name_table.names[self.name_idx].name
        self.wrapS = GXTexWrapMode(self.wrap & 3)
        self.wrapT = GXTexWrapMode((self.wrap >> 2) & 3)
        return super().to_json()

    def to_bytes(self) -> bytes:
        self.name_idx = self.get_parent(AnimationTex).name_table.add_entry(self.texture_name)
        self.wrap = self.wrapS.value | (self.wrapT.value << 2)
        return super().to_bytes()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.texture_name == other.texture_name and \
                   self.wrapS == other.wrapS and \
                   self.wrapT == other.wrapT and \
                   self.reverse_mode == other.reverse_mode
        else:
            return False


class AnimationTexRangeRandomKey(Structure):
    idx = u16('H2x')


class AnimationTexKey(KeyFrameBase):
    def get_frame_data(self, _) -> Field:
        if self.value_type == KeyType.Random or self.value_type == KeyType.Range:
            return StructField(AnimationTexRangeRandomKey, True)
        else:
            return StructField(AnimationTexParam, True)

    padd = padding(8)
    data = UnionField(get_frame_data)


class AnimationTexRange(Structure):
    param = StructField(AnimationTexParam)
    flip_random = FlagEnumField(FlipRandom)
    padd = padding(3)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.param == other.param and self.flip_random == other.flip_random
        else:
            return False

##################
# Parsed Formats #
##################

class AnimationTexFrame(KeyFrameBase):
    def has_data(self, _) -> bool:
        return self.value_type != KeyType.Random

    def has_flip_random(self, _) -> bool:
        return self.value_type == KeyType.Range

    data = StructField(AnimationTexParam, True, cond=has_data)
    flip_random = FlagEnumField(FlipRandom, cond=has_flip_random)


class AnimationTex(Structure):
    def get_key_count(self) -> int:
        return self.key_table.entry_count

    def has_range_table(self, is_json: bool) -> bool:
        return not is_json and get_anim_header(self).range_table_size != 0

    def get_range_count(self) -> int:
        return self.range_table.entry_count

    def has_random_table(self, is_json: bool) -> bool:
        return not is_json and get_anim_header(self).random_table_size != 0

    def has_random_pool(self, is_json: bool) -> bool:
        return is_json or self.has_random_table(is_json)

    def get_random_count(self) -> int:
        return self.random_table.entry_count

    key_table = StructField(AnimDataTable, cond=skip_json)
    keys = ListField(StructField(AnimationTexKey), get_key_count, cond=skip_json)
    frames = ListField(StructField(AnimationTexFrame), cond=skip_binary) # Parsed version

    range_table = StructField(AnimDataTable, cond=has_range_table)
    ranges = ListField(StructField(AnimationTexRange), get_range_count, cond=has_range_table)

    random_table = StructField(AnimDataTable, cond=has_random_table)
    random_pool = ListField(StructField(AnimationTexParam), get_random_count, cond=has_random_pool)

    name_table = StructField(NameTable, alignment=4, cond=skip_json)

    def to_json(self) -> dict[str, Any]:

        # Parse each key
        for key in self.keys:

            # Create the parsed value
            parsed_frame = AnimationTexFrame(self)
            parsed_frame.frame = key.frame
            parsed_frame.value_type = key.value_type

            # Copy the data depending on the frame type
            if key.value_type == KeyType.Fixed:
                parsed_frame.data = key.data
            elif key.value_type == KeyType.Range:
                data: AnimationTexRange = self.ranges[key.data.idx]
                parsed_frame.data = data.param
                parsed_frame.flip_random = data.flip_random

            # Append frame
            self.frames.append(parsed_frame)

        # Let the parser do the rest
        return super().to_json()


    def to_bytes(self) -> bytes:

        # Iterate frames
        for i, frame in enumerate(self.frames):

            # Create key and copy basic info
            key = AnimationTexKey(self)
            key.frame = frame.frame
            key.value_type = frame.value_type

            # Detect key format
            AnimationTexKey.data.detect_field(key, False)

            # Fixed frame
            if key.value_type == KeyType.Fixed:
                key.data = frame.data

            # Range frame
            elif key.value_type == KeyType.Range:
                range_entry = AnimationTexRange(self)
                range_entry.param = frame.data
                range_entry.flip_random = frame.flip_random
                key.data = AnimationTexRangeRandomKey(key)
                key.data.idx = self.add_range(range_entry)

            # Random frame
            else:
                key.data = AnimationTexRangeRandomKey(key)
                key.data.idx = i

            # Append new key
            self.keys.append(key)

        # Calculate the key table length and size
        anim_header = get_anim_header(self)
        self.key_table.entry_count = len(self.keys)
        anim_header.key_table_size = self.size(AnimationTex.key_table, AnimationTex.keys)

        # Calculate the range table length and size (if applicable)
        if self.ranges:
            self.range_table.entry_count = len(self.ranges)
            anim_header.range_table_size = self.size(AnimationTex.range_table, AnimationTex.ranges)
        else:
            anim_header.range_table_size = 0

        # Calculate the random table length and size (if applicable)
        if self.random_pool:
            self.random_table.entry_count = len(self.random_pool)
            anim_header.random_table_size = self.size(AnimationTex.random_table, AnimationTex.random_pool)
        else:
            anim_header.random_table_size = 0

        # Encode result (automatically updates name table)
        result = super().to_bytes()

        # Calculate name table size and return encoded data
        anim_header.name_table_size = self.size(AnimationTex.name_table, AnimationTex.name_table)
        return result

    def add_range(self, new_range: AnimationTexRange) -> int:
        for i, range in enumerate(self.ranges):
            if new_range == range:
                return i

        self.ranges.append(new_range)
        return len(self.ranges) - 1
