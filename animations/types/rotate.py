#!/usr/bin/env python3

# rotate.py
# Particle rotation animation definitions

from common.common import pascal_to_snake
from common.field import *
from animations.common import *
from animations.tables import *

###############
# Key Formats #
###############

class AnimationRotateKeyFixed(Structure):
    values = ListField(f32(), get_sub_target_count)

class AnimationRotateKeyRangeRandom(Structure):
    def get_padding(self) -> int:
        param_size = get_sub_target_count(self) * 4
        return 0xC + param_size - 0xE

    idx = u16() # For random keyframes, this is just the index into the key frame list
    padd = ListField(u8(), get_padding, cond=skip_json)


class AnimationRotateKey(KeyFrameBase):
    def get_key_data(self, _) -> Field:
        if self.value_type == KeyType.Fixed:
            return StructField(AnimationRotateKeyFixed, True)
        else:
            return StructField(AnimationRotateKeyRangeRandom, True)

    curve_types = ListField(StructField(KeyCurve), 8)
    key_data = UnionField(get_key_data)

################
# Range Values #
################

class AnimationRotateRanges(Structure):
    values = ListField(f32(), lambda self: 2 * get_sub_target_count(self))
    random_rotation_direction = boolean('?3x')

##################
# Parsed Formats #
##################

class AnimationRotateTarget(Structure):
    def has_value(self, _) -> bool:
        return get_key_type(self) == KeyType.Fixed

    def has_range(self, _) -> bool:
        return get_key_type(self) == KeyType.Range

    interpolation = StructField(KeyCurve, unroll=True)
    value = f32(cond=has_value)
    range = ListField(f32(), 2, cond=has_range)


class AnimationRotateFrame(KeyFrameBase):
    def has_random_rotation_dir(self, _) -> bool:
        return self.value_type == KeyType.Range

    def has_x_target(self, _) -> bool:
        return self.x is not None

    def has_y_target(self, _) -> bool:
        return self.y is not None

    def has_z_target(self, _) -> bool:
        return self.z is not None

    random_rotation_direction = boolean('?3x', cond=has_random_rotation_dir)
    x = StructField(AnimationRotateTarget, cond=has_x_target)
    y = StructField(AnimationRotateTarget, cond=has_y_target)
    z = StructField(AnimationRotateTarget, cond=has_z_target)


class AnimationRotateRandomPoolEntry(Structure):
    def has_x_target(self, _) -> bool:
        return self.x is not None

    def has_y_target(self, _) -> bool:
        return self.y is not None

    def has_z_target(self, _) -> bool:
        return self.z is not None

    random_rotation_direction = boolean('?3x')
    x = StructField(AnimationRotateTarget, cond=has_x_target)
    y = StructField(AnimationRotateTarget, cond=has_y_target)
    z = StructField(AnimationRotateTarget, cond=has_z_target)

###############
# Main Format #
###############

class AnimationRotate(Structure):
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
    frames = ListField(StructField(AnimationRotateKey), get_key_count, cond=skip_json)
    key_frames = ListField(StructField(AnimationRotateFrame), cond=skip_binary) # Parsed version

    range_table = StructField(AnimDataTable, cond=has_range_table)
    range_values = ListField(StructField(AnimationRotateRanges), get_range_count, cond=has_range_table)

    random_table = StructField(AnimDataTable, cond=has_random_table)
    random_values = ListField(StructField(AnimationRotateRanges), get_random_count, cond=has_random_table)
    random_pool = ListField(StructField(AnimationRotateRandomPoolEntry, True), cond=skip_binary) # Parsed version

    def decode(self) -> None:

        # Get targets
        sub_targets = get_anim_header(self).sub_targets

        # Parse each frame
        for frame in self.frames:

            # Copy the basic info
            parsed_frame = AnimationRotateFrame(self)
            parsed_frame.frame = frame.frame
            parsed_frame.value_type = frame.value_type

            # Copy the random rotation direction value
            if frame.value_type == KeyType.Range:
                range_idx = frame.key_data.idx
                parsed_frame.random_rotation_direction = self.range_values[range_idx].random_rotation_direction

            # Parse the enabled targets
            for i, target_name, target_value in get_enabled_targets(sub_targets):

                # Create the target and insert it into the data
                target_data = AnimationRotateTarget(parsed_frame)
                setattr(parsed_frame, pascal_to_snake(target_name), target_data)

                # Get the interpolation and value/range
                target_data.interpolation = frame.curve_types[target_value.bit_length() - 1]
                if parsed_frame.value_type == KeyType.Fixed:
                    target_data.value = frame.key_data.values[i]
                elif parsed_frame.value_type == KeyType.Range:
                    range_idx = frame.key_data.idx
                    range_values: AnimationRotateRanges = self.range_values[range_idx]
                    target_data.range = range_values.values[i*2 : i*2 + 2]

            # Add the parsed frame to the list
            self.key_frames.append(parsed_frame)

        # Parse the random pool entries
        for entry in self.random_values:

            # Create parsed entry
            pool_entry = AnimationRotateRandomPoolEntry(self)
            for i, target_name, target_value in get_enabled_targets(sub_targets):
                setattr(pool_entry, pascal_to_snake(target_name), entry.values[i*2 : i*2 + 2])

            # Add the new entry
            self.random_pool.append(pool_entry)

        # Do decoding
        super().decode()

    def encode(self) -> None:

        # Get the enabled targets
        anim_header = get_anim_header(self)
        sub_targets = anim_header.sub_targets
        random_idx = 0

        # Parse the individual frames
        for frame in self.key_frames:

            # Create the key and copy the basic info
            key = AnimationRotateKey(self)
            key.frame = frame.frame
            key.value_type = frame.value_type
            key.curve_types = [KeyCurve(key)] * 8 # Default values

            # Detect the key format
            AnimationRotateKey.key_data.detect_field(key, False)

            # Fixed frame
            if key.value_type == KeyType.Fixed:
                data = AnimationRotateKeyFixed(key)

                # Combine the values and interpolation types
                for _, target_name, target_value in get_enabled_targets(sub_targets):
                    target: AnimationRotateTarget = getattr(frame, pascal_to_snake(target_name))
                    data.values.append(target.value)
                    key.curve_types[target_value.bit_length() - 1] = target.interpolation

            # Range frame
            elif key.value_type == KeyType.Range:

                # Create data structures
                data = AnimationRotateKeyRangeRandom(key)
                range = AnimationRotateRanges(self)
                range.random_rotation_direction = frame.random_rotation_direction

                # Combine the range values and interpolation types
                for _, target_name, target_value in get_enabled_targets(sub_targets):
                    target: AnimationRotateTarget = getattr(frame, pascal_to_snake(target_name))
                    key.curve_types[target_value.bit_length() - 1] = target.interpolation
                    range.values += target.range

                # Get the index in the range table and fill the padding
                data.idx = self.add_range(range)
                data.padd = [0] * data.get_padding()

            # Random frame
            else:
                data = AnimationRotateKeyRangeRandom(key)

                # Get the index in the key table and fill the padding
                data.idx = random_idx
                data.padd = [0] * data.get_padding()
                random_idx += 1

                # Fill curve types
                for _, target_name, target_value in get_enabled_targets(sub_targets):
                    target: AnimationRotateTarget = getattr(frame, pascal_to_snake(target_name))
                    key.curve_types[target_value.bit_length() - 1] = target.interpolation

            # Insert the data and add the key to the list
            key.key_data = data
            self.frames.append(key)

        # Fill the random pool if not empty
        for entry in self.random_pool:
            random = AnimationRotateRanges(self)
            random.random_rotation_direction = entry.random_rotation_direction
            for target in sub_targets:
                target: list = getattr(entry, pascal_to_snake(target.name))
                random.values += target
            self.random_values.append(random)
            random_table_size += random.size()

        # Calculate the key table length and size
        self.frame_table = AnimDataTable(self)
        self.frame_table.entry_count = len(self.frames)
        anim_header.key_table_size = self.size(AnimationRotate.frame_table, AnimationRotate.frames)

        # Calculate the range table length and size (if applicable)
        if self.range_values:
            self.range_table = AnimDataTable(self)
            self.range_table.entry_count = len(self.range_values)
            anim_header.range_table_size = self.size(AnimationRotate.range_table, AnimationRotate.range_values, True)

        # Calculate the random table length and size (if applicable)
        if self.random_values:
            self.random_table = AnimDataTable(self)
            self.random_table.entry_count = len(self.random_values)
            anim_header.random_table_size = self.size(AnimationRotate.random_table, AnimationRotate.random_values, True)

        # Do encoding
        super().encode()

    def add_range(self, range: AnimationRotateRanges) -> int:
        for i, entry in enumerate(self.range_values):
            if range.values == entry.values and range.random_rotation_direction == entry.random_rotation_direction:
                return i

        self.range_values.append(range)
        return len(self.range_values) - 1
