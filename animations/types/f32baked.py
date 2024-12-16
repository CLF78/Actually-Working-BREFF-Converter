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
