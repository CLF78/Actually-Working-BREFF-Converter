#!/usr/bin/env python3

# f32.py
# Particle F32 animation definitions

from typing import Any
from common.common import pascal_to_snake
from common.field import *
from animations.common import *
from animations.tables import *
from animations.flags import *

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
    def get_key_data(self) -> Field:
        if self.value_type == KeyType.Fixed:
            return StructField(AnimationF32KeyFixed, True)
        else:
            return StructField(AnimationF32KeyRangeRandom, True)

    curve_types = ListField(EnumField(KeyCurveType, mask=KeyCurveType.Mask), 8)
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

    interpolation = EnumField(KeyCurveType, mask=KeyCurveType.Mask)
    value = f32(cond=has_value)
    range = ListField(f32(), 2, cond=has_range)


class AnimationF32Frame(KeyFrameBase):
    def has_x_target(self, _) -> bool:
        return check_enabled_target(self, AnimationVec2Targets.X) or \
               check_enabled_target(self, AnimationVec3Targets.X)

    def has_y_target(self, _) -> bool:
        return check_enabled_target(self, AnimationVec2Targets.Y) or \
               check_enabled_target(self, AnimationVec3Targets.Y)

    def has_z_target(self, _) -> bool:
        return check_enabled_target(self, AnimationVec3Targets.Z)

    def has_x_size_target(self, _) -> bool:
        return check_enabled_target(self, AnimationDiscParamTargets.XSize) or \
               check_enabled_target(self, AnimationCubeParamTargets.XSize) or \
               check_enabled_target(self, AnimationCylinderSphereTorusParamTargets.XSize)

    def has_y_size_target(self, _) -> bool:
        return check_enabled_target(self, AnimationCubeParamTargets.YSize) or \
               check_enabled_target(self, AnimationCylinderSphereTorusParamTargets.YSize)

    def has_z_size_target(self, _) -> bool:
        return check_enabled_target(self, AnimationDiscParamTargets.ZSize) or \
               check_enabled_target(self, AnimationCubeParamTargets.ZSize) or \
               check_enabled_target(self, AnimationCylinderSphereTorusParamTargets.ZSize)

    def has_x_rot_target(self, _) -> bool:
        return check_enabled_target(self, AnimationLineParamTargets.XRot) or \
               check_enabled_target(self, AnimationFieldGravityTargets.XRot) or \
               check_enabled_target(self, AnimationFieldSpinTargets.XRot)

    def has_y_rot_target(self, _) -> bool:
        return check_enabled_target(self, AnimationLineParamTargets.YRot) or \
               check_enabled_target(self, AnimationFieldGravityTargets.YRot) or \
               check_enabled_target(self, AnimationFieldSpinTargets.YRot)

    def has_z_rot_target(self, _) -> bool:
        return check_enabled_target(self, AnimationLineParamTargets.ZRot) or \
               check_enabled_target(self, AnimationFieldGravityTargets.ZRot) or \
               check_enabled_target(self, AnimationFieldSpinTargets.ZRot)

    def has_inner_radius_target(self, _) -> bool:
        return check_enabled_target(self, AnimationDiscParamTargets.InnerRadius) or \
               check_enabled_target(self, AnimationCubeParamTargets.InnerRadius) or \
               check_enabled_target(self, AnimationCylinderSphereTorusParamTargets.InnerRadius)

    def has_angle_start_target(self, _) -> bool:
        return check_enabled_target(self, AnimationDiscParamTargets.AngleStart) or \
               check_enabled_target(self, AnimationCylinderSphereTorusParamTargets.AngleStart)

    def has_angle_end_target(self, _) -> bool:
        return check_enabled_target(self, AnimationDiscParamTargets.AngleEnd) or \
               check_enabled_target(self, AnimationCylinderSphereTorusParamTargets.AngleEnd)

    def has_length_target(self, _) -> bool:
        return check_enabled_target(self, AnimationLineParamTargets.Length)

    def has_power_target(self, _) -> bool:
        return check_enabled_target(self, AnimationFieldGravityTargets.Power) or \
               check_enabled_target(self, AnimationFieldRandomTargets.Power) or \
               check_enabled_target(self, AnimationFieldMagnetTargets.Power) or \
               check_enabled_target(self, AnimationFieldNewtonTargets.Power)

    def has_diffusion_target(self, _) -> bool:
        return check_enabled_target(self, AnimationFieldRandomTargets.Diffusion)

    def has_speed_target(self, _) -> bool:
        return check_enabled_target(self, AnimationFieldSpinTargets.Speed)

    def has_distance_target(self, _) -> bool:
        return check_enabled_target(self, AnimationFieldVortexTargets.Distance)

    def has_ref_distance_target(self, _) -> bool:
        return check_enabled_target(self, AnimationFieldNewtonTargets.RefDistance)

    def has_inner_speed_target(self, _) -> bool:
        return check_enabled_target(self, AnimationFieldVortexTargets.InnerSpeed)

    def has_outer_speed_target(self, _) -> bool:
        return check_enabled_target(self, AnimationFieldVortexTargets.OuterSpeed)

    def has_x_trans_target(self, _) -> bool:
        return check_enabled_target(self, AnimationFieldMagnetTargets.XTrans) or \
               check_enabled_target(self, AnimationFieldNewtonTargets.XTrans) or \
               check_enabled_target(self, AnimationFieldVortexTargets.XTrans)

    def has_y_trans_target(self, _) -> bool:
        return check_enabled_target(self, AnimationFieldMagnetTargets.YTrans) or \
               check_enabled_target(self, AnimationFieldNewtonTargets.YTrans) or \
               check_enabled_target(self, AnimationFieldVortexTargets.YTrans)

    def has_z_trans_target(self, _) -> bool:
        return check_enabled_target(self, AnimationFieldMagnetTargets.ZTrans) or \
               check_enabled_target(self, AnimationFieldNewtonTargets.ZTrans) or \
               check_enabled_target(self, AnimationFieldVortexTargets.ZTrans)

    def has_power_spec_dir_target(self, _) -> bool:
        return check_enabled_target(self, AnimationEmitterSpeedSpecDirTargets.PowerSpecDir)

    def has_diffusion_spec_dir_target(self, _) -> bool:
        return check_enabled_target(self, AnimationEmitterSpeedSpecDirTargets.DiffusionSpecDir)

    def has_vel_spec_dir_x_target(self, _) -> bool:
        return check_enabled_target(self, AnimationEmitterSpeedSpecDirTargets.VelSpecDirX)

    def has_vel_spec_dir_y_target(self, _) -> bool:
        return check_enabled_target(self, AnimationEmitterSpeedSpecDirTargets.VelSpecDirY)

    def has_vel_spec_dir_z_target(self, _) -> bool:
        return check_enabled_target(self, AnimationEmitterSpeedSpecDirTargets.VelSpecDirZ)

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
        return check_enabled_target(self, AnimationVec2Targets.X) or \
               check_enabled_target(self, AnimationVec3Targets.X)

    def has_y_target(self, _) -> bool:
        return check_enabled_target(self, AnimationVec2Targets.Y) or \
               check_enabled_target(self, AnimationVec3Targets.Y)

    def has_z_target(self, _) -> bool:
        return check_enabled_target(self, AnimationVec3Targets.Z)

    def has_x_size_target(self, _) -> bool:
        return check_enabled_target(self, AnimationDiscParamTargets.XSize) or \
               check_enabled_target(self, AnimationCubeParamTargets.XSize) or \
               check_enabled_target(self, AnimationCylinderSphereTorusParamTargets.XSize)

    def has_y_size_target(self, _) -> bool:
        return check_enabled_target(self, AnimationCubeParamTargets.YSize) or \
               check_enabled_target(self, AnimationCylinderSphereTorusParamTargets.YSize)

    def has_z_size_target(self, _) -> bool:
        return check_enabled_target(self, AnimationDiscParamTargets.ZSize) or \
               check_enabled_target(self, AnimationCubeParamTargets.ZSize) or \
               check_enabled_target(self, AnimationCylinderSphereTorusParamTargets.ZSize)

    def has_x_rot_target(self, _) -> bool:
        return check_enabled_target(self, AnimationLineParamTargets.XRot) or \
               check_enabled_target(self, AnimationFieldGravityTargets.XRot) or \
               check_enabled_target(self, AnimationFieldSpinTargets.XRot)

    def has_y_rot_target(self, _) -> bool:
        return check_enabled_target(self, AnimationLineParamTargets.YRot) or \
               check_enabled_target(self, AnimationFieldGravityTargets.YRot) or \
               check_enabled_target(self, AnimationFieldSpinTargets.YRot)

    def has_z_rot_target(self, _) -> bool:
        return check_enabled_target(self, AnimationLineParamTargets.ZRot) or \
               check_enabled_target(self, AnimationFieldGravityTargets.ZRot) or \
               check_enabled_target(self, AnimationFieldSpinTargets.ZRot)

    def has_inner_radius_target(self, _) -> bool:
        return check_enabled_target(self, AnimationDiscParamTargets.InnerRadius) or \
               check_enabled_target(self, AnimationCubeParamTargets.InnerRadius) or \
               check_enabled_target(self, AnimationCylinderSphereTorusParamTargets.InnerRadius)

    def has_angle_start_target(self, _) -> bool:
        return check_enabled_target(self, AnimationDiscParamTargets.AngleStart) or \
               check_enabled_target(self, AnimationCylinderSphereTorusParamTargets.AngleStart)

    def has_angle_end_target(self, _) -> bool:
        return check_enabled_target(self, AnimationDiscParamTargets.AngleEnd) or \
               check_enabled_target(self, AnimationCylinderSphereTorusParamTargets.AngleEnd)

    def has_length_target(self, _) -> bool:
        return check_enabled_target(self, AnimationLineParamTargets.Length)

    def has_power_target(self, _) -> bool:
        return check_enabled_target(self, AnimationFieldGravityTargets.Power) or \
               check_enabled_target(self, AnimationFieldRandomTargets.Power) or \
               check_enabled_target(self, AnimationFieldMagnetTargets.Power) or \
               check_enabled_target(self, AnimationFieldNewtonTargets.Power)

    def has_diffusion_target(self, _) -> bool:
        return check_enabled_target(self, AnimationFieldRandomTargets.Diffusion)

    def has_speed_target(self, _) -> bool:
        return check_enabled_target(self, AnimationFieldSpinTargets.Speed)

    def has_distance_target(self, _) -> bool:
        return check_enabled_target(self, AnimationFieldVortexTargets.Distance)

    def has_ref_distance_target(self, _) -> bool:
        return check_enabled_target(self, AnimationFieldNewtonTargets.RefDistance)

    def has_inner_speed_target(self, _) -> bool:
        return check_enabled_target(self, AnimationFieldVortexTargets.InnerSpeed)

    def has_outer_speed_target(self, _) -> bool:
        return check_enabled_target(self, AnimationFieldVortexTargets.OuterSpeed)

    def has_x_trans_target(self, _) -> bool:
        return check_enabled_target(self, AnimationFieldMagnetTargets.XTrans) or \
               check_enabled_target(self, AnimationFieldNewtonTargets.XTrans) or \
               check_enabled_target(self, AnimationFieldVortexTargets.XTrans)

    def has_y_trans_target(self, _) -> bool:
        return check_enabled_target(self, AnimationFieldMagnetTargets.YTrans) or \
               check_enabled_target(self, AnimationFieldNewtonTargets.YTrans) or \
               check_enabled_target(self, AnimationFieldVortexTargets.YTrans)

    def has_z_trans_target(self, _) -> bool:
        return check_enabled_target(self, AnimationFieldMagnetTargets.ZTrans) or \
               check_enabled_target(self, AnimationFieldNewtonTargets.ZTrans) or \
               check_enabled_target(self, AnimationFieldVortexTargets.ZTrans)

    def has_power_spec_dir_target(self, _) -> bool:
        return check_enabled_target(self, AnimationEmitterSpeedSpecDirTargets.PowerSpecDir)

    def has_diffusion_spec_dir_target(self, _) -> bool:
        return check_enabled_target(self, AnimationEmitterSpeedSpecDirTargets.DiffusionSpecDir)

    def has_vel_spec_dir_x_target(self, _) -> bool:
        return check_enabled_target(self, AnimationEmitterSpeedSpecDirTargets.VelSpecDirX)

    def has_vel_spec_dir_y_target(self, _) -> bool:
        return check_enabled_target(self, AnimationEmitterSpeedSpecDirTargets.VelSpecDirY)

    def has_vel_spec_dir_z_target(self, _) -> bool:
        return check_enabled_target(self, AnimationEmitterSpeedSpecDirTargets.VelSpecDirZ)

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

    def to_json(self) -> dict[str, Any]:

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

        # Let the parser do the rest
        return super().to_json()
