#!/usr/bin/env python3

# f32.py
# Particle F32 animation definitions

from common.common import pascal_to_snake
from common.field import *
from animations.common import *
from animations.tables import *

###############
# Key Formats #
###############

class AnimationF32KeyFixed(Structure):
    values = ListField(f32(), get_sub_target_count)

class AnimationF32KeyRangeRandom(Structure):
    def get_padding(self) -> int:
        param_size = get_sub_target_count(self) * 4
        return 0xC + param_size - 0xE

    idx = u16() # For random keyframes, this is just the index into the key frame list
    padd = ListField(u8(), get_padding, cond=skip_json)


class AnimationF32Key(KeyFrameBase):
    def get_key_data(self, _) -> Field:
        if self.value_type == KeyType.Fixed:
            return StructField(AnimationF32KeyFixed, True)
        else:
            return StructField(AnimationF32KeyRangeRandom, True)

    curve_types = ListField(StructField(KeyCurve), 8)
    key_data = UnionField(get_key_data)

################
# Range Values #
################

class AnimationF32Ranges(Structure):
    values = ListField(f32(), lambda self: 2 * get_sub_target_count(self))

########################
# Parsed Frame Formats #
########################

class AnimationF32Target(Structure):
    def has_value(self, _) -> bool:
        return get_key_type(self) == KeyType.Fixed

    def has_range(self, _) -> bool:
        return get_key_type(self) == KeyType.Range

    interpolation = StructField(KeyCurve, unroll=True)
    value = f32(cond=has_value)
    range = ListField(f32(), 2, cond=has_range)


class AnimationF32Frame(KeyFrameBase):
    def has_x_target(self, _) -> bool:
        return self.x is not None

    def has_y_target(self, _) -> bool:
        return self.y is not None

    def has_z_target(self, _) -> bool:
        return self.z is not None

    def has_x_size_target(self, _) -> bool:
        return self.x_size is not None

    def has_y_size_target(self, _) -> bool:
        return self.y_size is not None

    def has_z_size_target(self, _) -> bool:
        return self.z_size is not None

    def has_x_rot_target(self, _) -> bool:
        return self.x_rot is not None

    def has_y_rot_target(self, _) -> bool:
        return self.y_rot is not None

    def has_z_rot_target(self, _) -> bool:
        return self.z_rot is not None

    def has_inner_radius_target(self, _) -> bool:
        return self.inner_radius is not None

    def has_angle_start_target(self, _) -> bool:
        return self.angle_start is not None

    def has_angle_end_target(self, _) -> bool:
        return self.angle_end is not None

    def has_length_target(self, _) -> bool:
        return self.length is not None

    def has_power_target(self, _) -> bool:
        return self.power is not None

    def has_diffusion_target(self, _) -> bool:
        return self.diffusion is not None

    def has_speed_target(self, _) -> bool:
        return self.speed is not None

    def has_distance_target(self, _) -> bool:
        return self.distance is not None

    def has_ref_distance_target(self, _) -> bool:
        return self.ref_distance is not None

    def has_inner_speed_target(self, _) -> bool:
        return self.inner_speed is not None

    def has_outer_speed_target(self, _) -> bool:
        return self.outer_speed is not None

    def has_x_trans_target(self, _) -> bool:
        return self.x_trans is not None

    def has_y_trans_target(self, _) -> bool:
        return self.y_trans is not None

    def has_z_trans_target(self, _) -> bool:
        return self.z_trans is not None

    def has_power_spec_dir_target(self, _) -> bool:
        return self.power_spec_dir is not None

    def has_diffusion_spec_dir_target(self, _) -> bool:
        return self.diffusion_spec_dir is not None

    def has_vel_spec_dir_x_target(self, _) -> bool:
        return self.vel_spec_dir_x is not None

    def has_vel_spec_dir_y_target(self, _) -> bool:
        return self.vel_spec_dir_y is not None

    def has_vel_spec_dir_z_target(self, _) -> bool:
        return self.vel_spec_dir_z is not None

    t = StructField(AnimationF32Target, True, cond=has_single_target)

    x = StructField(AnimationF32Target, cond=has_x_target)
    y = StructField(AnimationF32Target, cond=has_y_target)
    z = StructField(AnimationF32Target, cond=has_z_target)

    x_size = StructField(AnimationF32Target, cond=has_x_size_target)
    y_size = StructField(AnimationF32Target, cond=has_y_size_target)
    z_size = StructField(AnimationF32Target, cond=has_z_size_target)

    x_rot = StructField(AnimationF32Target, cond=has_x_rot_target)
    y_rot = StructField(AnimationF32Target, cond=has_y_rot_target)
    z_rot = StructField(AnimationF32Target, cond=has_z_rot_target)

    inner_radius = StructField(AnimationF32Target, cond=has_inner_radius_target)
    angle_start = StructField(AnimationF32Target, cond=has_angle_start_target)
    angle_end = StructField(AnimationF32Target, cond=has_angle_end_target)

    length = StructField(AnimationF32Target, cond=has_length_target)

    power = StructField(AnimationF32Target, cond=has_power_target)
    diffusion = StructField(AnimationF32Target, cond=has_diffusion_target)
    speed = StructField(AnimationF32Target, cond=has_speed_target)
    distance = StructField(AnimationF32Target, cond=has_distance_target)

    x_trans = StructField(AnimationF32Target, cond=has_x_trans_target)
    y_trans = StructField(AnimationF32Target, cond=has_y_trans_target)
    z_trans = StructField(AnimationF32Target, cond=has_z_trans_target)

    ref_distance = StructField(AnimationF32Target, cond=has_ref_distance_target)
    inner_speed = StructField(AnimationF32Target, cond=has_inner_speed_target)
    outer_speed = StructField(AnimationF32Target, cond=has_outer_speed_target)

    power_spec_dir = StructField(AnimationF32Target, cond=has_power_spec_dir_target)
    diffusion_spec_dir = StructField(AnimationF32Target, cond=has_diffusion_spec_dir_target)
    vel_spec_dir_x = StructField(AnimationF32Target, cond=has_vel_spec_dir_x_target)
    vel_spec_dir_y = StructField(AnimationF32Target, cond=has_vel_spec_dir_y_target)
    vel_spec_dir_z = StructField(AnimationF32Target, cond=has_vel_spec_dir_z_target)

####################################
# Parsed Random Pool Entry Formats #
####################################

class AnimationF32RandomPoolEntry(Structure):
    def has_x_target(self, _) -> bool:
        return self.x is not None

    def has_y_target(self, _) -> bool:
        return self.y is not None

    def has_z_target(self, _) -> bool:
        return self.z is not None

    def has_x_size_target(self, _) -> bool:
        return self.x_size is not None

    def has_y_size_target(self, _) -> bool:
        return self.y_size is not None

    def has_z_size_target(self, _) -> bool:
        return self.z_size is not None

    def has_x_rot_target(self, _) -> bool:
        return self.x_rot is not None

    def has_y_rot_target(self, _) -> bool:
        return self.y_rot is not None

    def has_z_rot_target(self, _) -> bool:
        return self.z_rot is not None

    def has_inner_radius_target(self, _) -> bool:
        return self.inner_radius is not None

    def has_angle_start_target(self, _) -> bool:
        return self.angle_start is not None

    def has_angle_end_target(self, _) -> bool:
        return self.angle_end is not None

    def has_length_target(self, _) -> bool:
        return self.length is not None

    def has_power_target(self, _) -> bool:
        return self.power is not None

    def has_diffusion_target(self, _) -> bool:
        return self.diffusion is not None

    def has_speed_target(self, _) -> bool:
        return self.speed is not None

    def has_distance_target(self, _) -> bool:
        return self.distance is not None

    def has_ref_distance_target(self, _) -> bool:
        return self.ref_distance is not None

    def has_inner_speed_target(self, _) -> bool:
        return self.inner_speed is not None

    def has_outer_speed_target(self, _) -> bool:
        return self.outer_speed is not None

    def has_x_trans_target(self, _) -> bool:
        return self.x_trans is not None

    def has_y_trans_target(self, _) -> bool:
        return self.y_trans is not None

    def has_z_trans_target(self, _) -> bool:
        return self.z_trans is not None

    def has_power_spec_dir_target(self, _) -> bool:
        return self.power_spec_dir is not None

    def has_diffusion_spec_dir_target(self, _) -> bool:
        return self.diffusion_spec_dir is not None

    def has_vel_spec_dir_x_target(self, _) -> bool:
        return self.vel_spec_dir_x is not None

    def has_vel_spec_dir_y_target(self, _) -> bool:
        return self.vel_spec_dir_y is not None

    def has_vel_spec_dir_z_target(self, _) -> bool:
        return self.vel_spec_dir_z is not None

    t = ListField(f32(), 2, cond=has_single_target)

    x = ListField(f32(), 2, cond=has_x_target)
    y = ListField(f32(), 2, cond=has_y_target)
    z = ListField(f32(), 2, cond=has_z_target)

    x_size = ListField(f32(), 2, cond=has_x_size_target)
    y_size = ListField(f32(), 2, cond=has_y_size_target)
    z_size = ListField(f32(), 2, cond=has_z_size_target)

    x_rot = ListField(f32(), 2, cond=has_x_rot_target)
    y_rot = ListField(f32(), 2, cond=has_y_rot_target)
    z_rot = ListField(f32(), 2, cond=has_z_rot_target)

    inner_radius = ListField(f32(), 2, cond=has_inner_radius_target)
    angle_start = ListField(f32(), 2, cond=has_angle_start_target)
    angle_end = ListField(f32(), 2, cond=has_angle_end_target)

    length = ListField(f32(), 2, cond=has_length_target)

    power = ListField(f32(), 2, cond=has_power_target)
    diffusion = ListField(f32(), 2, cond=has_diffusion_target)
    speed = ListField(f32(), 2, cond=has_speed_target)
    distance = ListField(f32(), 2, cond=has_distance_target)

    x_trans = ListField(f32(), 2, cond=has_x_trans_target)
    y_trans = ListField(f32(), 2, cond=has_y_trans_target)
    z_trans = ListField(f32(), 2, cond=has_z_trans_target)

    ref_distance = ListField(f32(), 2, cond=has_ref_distance_target)
    inner_speed = ListField(f32(), 2, cond=has_inner_speed_target)
    outer_speed = ListField(f32(), 2, cond=has_outer_speed_target)

    power_spec_dir = ListField(f32(), 2, cond=has_power_spec_dir_target)
    diffusion_spec_dir = ListField(f32(), 2, cond=has_diffusion_spec_dir_target)
    vel_spec_dir_x = ListField(f32(), 2, cond=has_vel_spec_dir_x_target)
    vel_spec_dir_y = ListField(f32(), 2, cond=has_vel_spec_dir_y_target)
    vel_spec_dir_z = ListField(f32(), 2, cond=has_vel_spec_dir_z_target)

###############
# Main Format #
###############

class AnimationF32(Structure):
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
    frames = ListField(StructField(AnimationF32Key), get_key_count, cond=skip_json)
    key_frames = ListField(StructField(AnimationF32Frame), cond=skip_binary) # Parsed version

    range_table = StructField(AnimDataTable, cond=has_range_table)
    range_values = ListField(StructField(AnimationF32Ranges), get_range_count, cond=has_range_table)

    random_table = StructField(AnimDataTable, cond=has_random_table)
    random_values = ListField(StructField(AnimationF32Ranges), get_random_count, cond=has_random_table)
    random_pool = ListField(StructField(AnimationF32RandomPoolEntry, True), cond=skip_binary) # Parsed version

    def decode(self) -> None:

        # Get the targets and the parameter names that might be necessary
        sub_targets = get_anim_header(self).sub_targets

        # Parse each frame
        for frame in self.frames:

            # Copy the basic info
            parsed_frame = AnimationF32Frame(self)
            parsed_frame.frame = frame.frame
            parsed_frame.value_type = frame.value_type

            # Parse the enabled targets
            for i, target_name, target_value in get_enabled_targets(sub_targets):

                # Create the target
                target_data = AnimationF32Target(parsed_frame)
                setattr(parsed_frame, pascal_to_snake(target_name), target_data)

                # Get the interpolation and value/range
                target_data.interpolation = frame.curve_types[target_value.bit_length() - 1]
                if parsed_frame.value_type == KeyType.Fixed:
                    target_data.value = frame.key_data.values[i]
                elif parsed_frame.value_type == KeyType.Range:
                    range_idx = frame.key_data.idx
                    range_values: AnimationF32Ranges = self.range_values[range_idx]
                    target_data.range = range_values.values[i*2 : i*2 + 2]

            # Add the parsed frame to the list
            self.key_frames.append(parsed_frame)

        # Parse the random pool entries
        for entry in self.random_values:

            # Create parsed entry
            pool_entry = AnimationF32RandomPoolEntry(self)
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
            key = AnimationF32Key(self)
            key.frame = frame.frame
            key.value_type = frame.value_type
            key.curve_types = [KeyCurve(key)] * 8 # Default values

            # Detect the key format
            AnimationF32Key.key_data.detect_field(key, False)

            # Fixed frame
            if key.value_type == KeyType.Fixed:
                data = AnimationF32KeyFixed(key)

                # Combine the values and interpolation types
                for _, target_name, target_value in get_enabled_targets(sub_targets):
                    target: AnimationF32Target = getattr(frame, pascal_to_snake(target_name))
                    data.values.append(target.value)
                    key.curve_types[target_value.bit_length() - 1] = target.interpolation

            # Range frame
            elif key.value_type == KeyType.Range:
                data = AnimationF32KeyRangeRandom(key)

                # Combine the range values and interpolation types
                range = AnimationF32Ranges()
                for _, target_name, target_value in get_enabled_targets(sub_targets):
                    target: AnimationF32Target = getattr(frame, pascal_to_snake(target_name))
                    key.curve_types[target_value.bit_length() - 1] = target.interpolation
                    range.values += target.range

                # Get the index in the range table and fill the padding
                data.idx = self.add_range(range)
                data.padd = [0] * data.get_padding()

            # Random frame
            else:
                data = AnimationF32KeyRangeRandom(key)

                # Get the index in the key table and fill the padding
                data.idx = random_idx
                data.padd = [0] * data.get_padding()
                random_idx += 1

                # Fill curve types
                for _, target_name, target_value in get_enabled_targets(sub_targets):
                    target: AnimationF32Target = getattr(frame, pascal_to_snake(target_name))
                    key.curve_types[target_value.bit_length() - 1] = target.interpolation

            # Insert the data and add the key to the list
            key.key_data = data
            self.frames.append(key)

        # Fill the random pool if not empty
        for entry in self.random_pool:
            random = AnimationF32Ranges(self)
            for target in sub_targets:
                target: list = getattr(entry, pascal_to_snake(target.name))
                random.values += target
            self.random_values.append(random)

        # Calculate the key table length and size
        self.frame_table = AnimDataTable(self)
        self.frame_table.entry_count = len(self.frames)
        anim_header.key_table_size = self.size(end_field=AnimationF32.frames)

        # Calculate the range table length and size (if applicable)
        if self.range_values:
            self.range_table = AnimDataTable(self)
            self.range_table.entry_count = len(self.range_values)
            anim_header.range_table_size = self.size(AnimationF32.range_table, AnimationF32.range_values, True)

        # Calculate the random table length and size (if applicable)
        if self.random_values:
            self.random_table = AnimDataTable(self)
            self.random_table.entry_count = len(self.random_values)
            anim_header.random_table_size = self.size(AnimationF32.random_table, AnimationF32.random_values, True)

        # Do encoding
        super().encode()

    def add_range(self, range: AnimationF32Ranges) -> int:
        for i, entry in enumerate(self.range_values):
            if range.values == entry.values:
                return i

        self.range_values.append(range)
        return len(self.range_values) - 1
