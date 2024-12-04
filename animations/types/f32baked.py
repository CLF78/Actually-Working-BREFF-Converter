#!/usr/bin/env python3

# f32baked.py
# Particle F32 baked animation definitions

from enum import IntFlag
from typing import Any
from common.field import *
from animations.tables import *
from animations.flags import *
from emitter.flags import EmitterShape

###########
# Helpers #
###########

def get_emitter(structure: Structure):
    from effect.effect import Effect
    return structure.get_parent(Effect).emitter

def get_anim_header(structure: Structure):
    from animations.header import AnimationHeader
    return structure.get_parent(AnimationHeader)

def get_param_count(structure: Structure) -> int:
    return get_anim_header(structure).get_param_count()

def check_enabled_target(structure: Structure, target: IntFlag) -> bool:
    return (get_anim_header(structure).kind_enable & target) != 0

def has_param1_target(self: Structure, _) -> bool:
    return check_enabled_target(self, AnimationF32ParamTargets.Param1)

def has_param2_target(self: Structure, _) -> bool:
    return check_enabled_target(self, AnimationF32ParamTargets.Param2)

def has_param3_target(self: Structure, _) -> bool:
    return check_enabled_target(self, AnimationF32ParamTargets.Param3)

def has_param4_target(self: Structure, _) -> bool:
    return check_enabled_target(self, AnimationF32ParamTargets.Param4)

def has_param5_target(self: Structure, _) -> bool:
    return check_enabled_target(self, AnimationF32ParamTargets.Param5)

def has_param6_target(self: Structure, _) -> bool:
    return check_enabled_target(self, AnimationF32ParamTargets.Param6)

##############
# Key Format #
##############

class AnimationF32BakedKey(Structure):
    values = ListField(f32(), get_param_count)

##################
# Parsed Formats #
##################

class AnimationF32BakedSingleFrame(Structure):
    def has_target(self, _) -> bool:
        return check_enabled_target(self, AnimationF32VectorTargets.X)

    x = f32(cond=has_target)


class AnimationF32BakedVectorFrame(Structure):
    def has_x_target(self, _) -> bool:
        return check_enabled_target(self, AnimationF32VectorTargets.X)

    def has_y_target(self, _) -> bool:
        return check_enabled_target(self, AnimationF32VectorTargets.Y)

    def has_z_target(self, _) -> bool:
        return check_enabled_target(self, AnimationF32VectorTargets.Z)

    x = f32(cond=has_x_target)
    y = f32(cond=has_y_target)
    z = f32(cond=has_z_target)


class AnimationF32BakedDiscParamsFrame(Structure):
    x_size = f32(cond=has_param1_target)
    inner_radius = f32(cond=has_param2_target)
    angle_start = f32(cond=has_param3_target)
    angle_end = f32(cond=has_param4_target)
    z_size = f32(cond=has_param5_target)


class AnimationF32BakedLineParamsFrame(Structure):
    length = f32(cond=has_param1_target)
    x_rot = f32(cond=has_param2_target)
    y_rot = f32(cond=has_param3_target)
    z_rot = f32(cond=has_param4_target)


class AnimationF32BakedCubeParamsFrame(Structure):
    x_size = f32(cond=has_param1_target)
    y_size = f32(cond=has_param2_target)
    z_size = f32(cond=has_param3_target)
    inner_radius = f32(cond=has_param4_target)


class AnimationF32BakedCylindereSphereTorusParamsFrame(Structure):
    x_size = f32(cond=has_param1_target)
    inner_radius = f32(cond=has_param2_target)
    angle_start = f32(cond=has_param3_target)
    angle_end = f32(cond=has_param4_target)
    y_size = f32(cond=has_param5_target)
    z_size = f32(cond=has_param6_target)


class AnimationF32BakedFrame(Structure):
    def get_frame_data(self) -> Field:
        single_target_anims = [AnimTargetF32.Texture1Rotation.name, AnimTargetF32.Texture2Rotation.name,
                            AnimTargetF32.TextureIndRotation.name, AnimTargetEmitterF32.EmitterEmissionRatio.name,
                            AnimTargetEmitterF32.EmitterSpeedOrig.name, AnimTargetEmitterF32.EmitterSpeedYAxis.name,
                            AnimTargetEmitterF32.EmitterSpeedRandom.name, AnimTargetEmitterF32.EmitterSpeedNormal.name,
                            AnimTargetEmitterF32.EmitterSpeedSpecDir]

        target = get_anim_header(self).target
        if target in single_target_anims:
            return StructField(AnimationF32BakedSingleFrame, True)
        elif target != AnimTargetEmitterF32.EmitterParam.name:
            return StructField(AnimationF32BakedVectorFrame, True)

        shape = get_emitter(self).emitter_flags.shape
        if shape == EmitterShape.Disc:
            return StructField(AnimationF32BakedDiscParamsFrame, True)
        elif shape == EmitterShape.Line:
            return StructField(AnimationF32BakedLineParamsFrame, True)
        elif shape == EmitterShape.Cube:
            return StructField(AnimationF32BakedCubeParamsFrame, True)
        elif shape != EmitterShape.Point:
            return StructField(AnimationF32BakedCylindereSphereTorusParamsFrame, True)
        else:
            raise ValueError('Emitter parameter animations are not supported by Point shaped emitters!')

    targets = UnionField(get_frame_data)

###############
# Main Format #
###############

class AnimationF32Baked(Structure):
    def get_key_count(self) -> int:
        return get_anim_header(self).frame_count

    def get_targets(self) -> IntFlag:
        if get_anim_header(self).target == AnimTargetEmitterF32.EmitterParam.name:
            return AnimationF32ParamTargets
        else:
            return AnimationF32VectorTargets

    keys = ListField(StructField(AnimationF32BakedKey), get_key_count, cond=skip_json)
    frames = ListField(StructField(AnimationF32BakedFrame, unroll=True), cond=skip_binary) # Parsed version

    def to_json(self) -> dict[str, Any]:

        # Get the targets and the parameter names that might be necessary
        targets = self.get_targets()
        emitter = get_emitter(self)
        emitter_shape = emitter.emitter_flags.shape
        param_names = list(emitter.shape_params._fields_.keys()) if emitter_shape != EmitterShape.Point else []

        # Parse each frame
        for key in self.keys:

            # Create the target container
            parsed_frame = AnimationF32BakedFrame(self)
            frame_data = AnimationF32BakedFrame.targets.detect_field(parsed_frame).struct_type(parsed_frame)
            parsed_frame.targets = frame_data

            # Parse the enabled targets
            i = 0
            for target in targets:
                if check_enabled_target(self, target):

                    # Get the target name
                    attr_name = target.name.lower()
                    if isinstance(target, AnimationF32ParamTargets):
                        attr_name = param_names[target.value.bit_length() - 1]

                    # Insert the value for the target
                    setattr(frame_data, attr_name, key.values[i])
                    i += 1

            # Add the parsed frame to the list
            self.frames.append(parsed_frame)

        # Let the parser do the rest
        return super().to_json()
