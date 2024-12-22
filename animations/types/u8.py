#!/usr/bin/env python3

# u8.py
# Particle U8 animation definitions

from common.common import pascal_to_snake
from common.field import *
from animations.common import *
from animations.tables import *

###############
# Key Formats #
###############

class AnimationU8KeyFixed(Structure):
    values = ListField(u8(), get_sub_target_count, alignment=2)


class AnimationU8KeyRangeRandom(Structure):
    def get_padding(self) -> int:
        param_count = get_sub_target_count(self)
        return align(0xC + param_count, 2) - 0xE

    idx = u16() # For random keyframes, this is just the index into the key frame list
    padd = ListField(u8(), get_padding, cond=skip_json)


class AnimationU8Key(KeyFrameBase):
    def get_key_data(self, _) -> Field:
        if self.value_type == KeyType.Fixed:
            return StructField(AnimationU8KeyFixed, True)
        else:
            return StructField(AnimationU8KeyRangeRandom, True)

    curve_types = ListField(EnumField(KeyCurveType, mask=KeyCurveType.Mask), 8)
    key_data = UnionField(get_key_data)

################
# Range Values #
################

class AnimationU8Ranges(Structure):
    values = ListField(u8(), lambda self: 2 * get_sub_target_count(self))

##################
# Parsed Formats #
##################

class AnimationU8Target(Structure):
    def has_value(self, _) -> bool:
        return get_key_type(self) == KeyType.Fixed

    def has_range(self, _) -> bool:
        return get_key_type(self) == KeyType.Range

    interpolation = EnumField(KeyCurveType, mask=KeyCurveType.Mask)
    value = u8(cond=has_value)
    range = ListField(u8(), 2, cond=has_range)


class AnimationU8Frame(KeyFrameBase):
    def has_r_target(self, _) -> bool:
        return self.r is not None

    def has_g_target(self, _) -> bool:
        return self.g is not None

    def has_b_target(self, _) -> bool:
        return self.b is not None

    r = StructField(AnimationU8Target, cond=has_r_target)
    g = StructField(AnimationU8Target, cond=has_g_target)
    b = StructField(AnimationU8Target, cond=has_b_target)
    t = StructField(AnimationU8Target, True, cond=has_single_target)


class AnimationU8RandomPoolEntry(Structure):
    def has_r_target(self, _) -> bool:
        return self.r is not None

    def has_g_target(self, _) -> bool:
        return self.g is not None

    def has_b_target(self, _) -> bool:
        return self.b is not None

    r = ListField(u8(), 2, cond=has_r_target)
    g = ListField(u8(), 2, cond=has_g_target)
    b = ListField(u8(), 2, cond=has_b_target)
    t = ListField(u8(), 2, cond=has_single_target)

###############
# Main Format #
###############

class AnimationU8(Structure):
    def get_key_count(self) -> int:
        return self.frame_table.entry_count

    def has_range_table(self, is_json: bool) -> bool:
        return not is_json and get_anim_header(self).range_table_size != 0

    def get_range_count(self) -> int:
        return self.range_table.entry_count

    def has_random_table(self, is_json: bool) -> bool:
        return not is_json and get_anim_header(self).random_table_size != 0

    def get_random_count(self) -> int:
        return self.random_table.entry_count

    frame_table = StructField(AnimDataTable, cond=skip_json)
    frames = ListField(StructField(AnimationU8Key), get_key_count, alignment=4, cond=skip_json)
    key_frames = ListField(StructField(AnimationU8Frame), cond=skip_binary) # Parsed version

    range_table = StructField(AnimDataTable, cond=has_range_table)
    range_values = ListField(StructField(AnimationU8Ranges), get_range_count, cond=has_range_table, alignment=4)

    random_table = StructField(AnimDataTable, cond=has_random_table)
    random_values = ListField(StructField(AnimationU8Ranges), get_random_count, cond=has_random_table, alignment=4)
    random_pool = ListField(StructField(AnimationU8RandomPoolEntry, True), cond=skip_binary) # Parsed version

    def decode(self) -> None:

        # Parse each frame
        sub_targets = get_anim_header(self).sub_targets
        for frame in self.frames:

            # Copy the basic info
            parsed_frame = AnimationU8Frame(self)
            parsed_frame.frame = frame.frame
            parsed_frame.value_type = frame.value_type

            # Parse the enabled targets
            for i, target_name, target_value in get_enabled_targets(sub_targets):

                # Create the target and insert it into the frame
                target_data = AnimationU8Target(parsed_frame)
                setattr(parsed_frame, pascal_to_snake(target_name), target_data)

                # Get the interpolation and value/range
                target_data.interpolation = frame.curve_types[target_value.bit_length() - 1]
                if parsed_frame.value_type == KeyType.Fixed:
                    target_data.value = frame.key_data.values[i]
                elif parsed_frame.value_type == KeyType.Range:
                    range_idx: int = frame.key_data.idx
                    range_values: AnimationU8Ranges = self.range_values[range_idx]
                    target_data.range = range_values.values[i*2 : i*2 + 2]

            # Add the parsed frame to the list
            self.key_frames.append(parsed_frame)

        # Parse the random pool entries
        for entry in self.random_values:

            # Create parsed entry
            pool_entry = AnimationU8RandomPoolEntry(self)
            for i, target_name, _ in get_enabled_targets(sub_targets):
                setattr(pool_entry, pascal_to_snake(target_name), entry.values[i*2 : i*2 + 2])

            # Add the new entry
            self.random_pool.append(pool_entry)

        # Do decoding
        super().decode()

    def encode(self) -> None:

        # Get the enabled targets
        anim_header = get_anim_header(self)
        sub_targets = anim_header.sub_targets

        # Parse the individual frames
        for i, frame in enumerate(self.key_frames):

            # Copy the basic info
            key = AnimationU8Key(self)
            key.frame = frame.frame
            key.value_type = frame.value_type
            key.curve_types = [KeyCurveType.Linear] * 8  # Default values

            # Detect the key format
            AnimationU8Key.key_data.detect_field(key, False)

            # Fixed frame
            if key.value_type == KeyType.Fixed:
                data = AnimationU8KeyFixed(key)

                # Combine the values and interpolation types
                for _, target_name, target_value in get_enabled_targets(sub_targets):
                    target: AnimationU8Target = getattr(frame, pascal_to_snake(target_name))
                    data.values.append(target.value)
                    key.curve_types[target_value.bit_length() - 1] = target.interpolation

            # Range frame
            elif key.value_type == KeyType.Range:
                data = AnimationU8KeyRangeRandom(key)

                # Combine the range values and interpolation types
                range = AnimationU8Ranges()
                for _, target_name, target_value in get_enabled_targets(sub_targets):
                    target: AnimationU8Target = getattr(frame, pascal_to_snake(target_name))
                    key.curve_types[target_value.bit_length() - 1] = target.interpolation
                    range.values += target.range

                # Get the index in the range table and fill the padding
                data.idx = self.add_range(range)
                data.padd = [0] * data.get_padding()

            # Random frame
            else:
                data = AnimationU8KeyRangeRandom(key)

                # Get the index in the key table and fill the padding
                data.idx = i
                data.padd = [0] * data.get_padding()

                # Fill curve types
                for _, target_name, target_value in get_enabled_targets(sub_targets):
                    target: AnimationU8Target = getattr(frame, pascal_to_snake(target_name))
                    key.curve_types[target_value.bit_length() - 1] = target.interpolation

            # Insert the data and add the key to the list
            key.key_data = data
            self.keys.append(key)

        # Fill the random pool if not empty
        for entry in self.random_pool:
            random = AnimationU8Ranges(self)
            for target in sub_targets:
                random.values += getattr(entry, pascal_to_snake(target.name))
            self.random_values.append(random)

        # Calculate the key table length and size
        self.frame_table.entry_count = len(self.frames)
        anim_header.key_table_size = self.size(AnimationU8.frame_table, AnimationU8.frames)

        # Calculate the range table length and size (if applicable)
        if self.range_values:
            self.range_table.entry_count = len(self.range_values)
            anim_header.range_table_size = self.size(AnimationU8.range_table, AnimationU8.range_values)

        # Calculate the random table length and size (if applicable)
        if self.random_values:
            self.random_table.entry_count = len(self.random_values)
            anim_header.random_table_size = self.size(AnimationU8.random_table, AnimationU8.random_values)

        # Do encoding
        super().encode()

    def add_range(self, range: AnimationU8Ranges) -> int:
        for i, entry in enumerate(self.range_values):
            if range.values == entry.values:
                return i

        self.range_values.append(range)
        return len(self.range_values) - 1
