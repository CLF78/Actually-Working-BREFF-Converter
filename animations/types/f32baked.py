#!/usr/bin/env python3

# f32baked.py
# Particle F32 baked animation definitions

from typing import Any
from common.common import pascal_to_snake
from common.field import *
from animations.common import *
from animations.flags import *
from animations.tables import *

##############
# Key Format #
##############

class AnimationF32BakedKey(Structure):
    values = ListField(f32(), get_sub_target_count)

##################
# Parsed Formats #
##################

class AnimationF32BakedFrame(Structure):
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

    t = f32(cond=has_single_target)

    x = f32(cond=has_x_target)
    y = f32(cond=has_y_target)
    z = f32(cond=has_z_target)

    x_size = f32(cond=has_x_size_target)
    y_size = f32(cond=has_y_size_target)
    z_size = f32(cond=has_z_size_target)

    x_rot = f32(cond=has_x_rot_target)
    y_rot = f32(cond=has_y_rot_target)
    z_rot = f32(cond=has_z_rot_target)

    inner_radius = f32(cond=has_inner_radius_target)
    angle_start = f32(cond=has_angle_start_target)
    angle_end = f32(cond=has_angle_end_target)

    length = f32(cond=has_length_target)

    power = f32(cond=has_power_target)
    diffusion = f32(cond=has_diffusion_target)
    speed = f32(cond=has_speed_target)
    distance = f32(cond=has_distance_target)

    x_trans = f32(cond=has_x_trans_target)
    y_trans = f32(cond=has_y_trans_target)
    z_trans = f32(cond=has_z_trans_target)

    ref_distance = f32(cond=has_ref_distance_target)
    inner_speed = f32(cond=has_inner_speed_target)
    outer_speed = f32(cond=has_outer_speed_target)

    power_spec_dir = f32(cond=has_power_spec_dir_target)
    diffusion_spec_dir = f32(cond=has_diffusion_spec_dir_target)
    vel_spec_dir_x = f32(cond=has_vel_spec_dir_x_target)
    vel_spec_dir_y = f32(cond=has_vel_spec_dir_y_target)
    vel_spec_dir_z = f32(cond=has_vel_spec_dir_z_target)

###############
# Main Format #
###############

class AnimationF32Baked(Structure):
    def get_key_count(self) -> int:
        return get_anim_header(self).frame_count

    keys = ListField(StructField(AnimationF32BakedKey), get_key_count, cond=skip_json)
    frames = ListField(StructField(AnimationF32BakedFrame, unroll=True), cond=skip_binary) # Parsed version

    def to_json(self) -> dict[str, Any]:

        # Get the targets and the parameter names that might be necessary
        sub_targets = get_anim_header(self).sub_targets

        # Parse each frame
        for key in self.keys:

            # Parse the enabled targets
            parsed_frame = AnimationF32BakedFrame(self)
            for i, target_name, _ in get_enabled_targets(sub_targets):
                setattr(parsed_frame, pascal_to_snake(target_name), key.values[i])

            # Add the parsed frame to the list
            self.frames.append(parsed_frame)

        # Let the parser do the rest
        return super().to_json()
