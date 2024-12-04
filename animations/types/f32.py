#!/usr/bin/env python3

# f32.py
# Particle F32 animation definitions

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

def get_key_type(structure: Structure) -> KeyType:
    return structure.get_parent(KeyFrameBase).value_type

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

###############
# Key Formats #
###############

class AnimationF32KeyFixed(Structure):
    values = ListField(f32(), get_param_count)

class AnimationF32KeyRangeRandom(Structure):
    def get_padding(self) -> int:
        param_size = get_anim_header(self).get_param_count() * 4
        return 0xC + param_size - 0xE

    idx = u16()
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
    values = ListField(f32(), lambda self: 2 * get_param_count(self))

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


class AnimationF32SingleTargetFrame(Structure):
    def has_target(self, _) -> bool:
        return check_enabled_target(self, AnimationF32VectorTargets.X)

    x = StructField(AnimationF32Target, True, cond=has_target)


class AnimationF32VectorFrame(Structure):
    def has_x_target(self, _) -> bool:
        return check_enabled_target(self, AnimationF32VectorTargets.X)

    def has_y_target(self, _) -> bool:
        return check_enabled_target(self, AnimationF32VectorTargets.Y)

    def has_z_target(self, _) -> bool:
        return check_enabled_target(self, AnimationF32VectorTargets.Z)

    x = StructField(AnimationF32Target, cond=has_x_target)
    y = StructField(AnimationF32Target, cond=has_y_target)
    z = StructField(AnimationF32Target, cond=has_z_target)


class AnimationF32DiscParamsFrame(Structure):
    x_size = StructField(AnimationF32Target, cond=has_param1_target)
    inner_radius = StructField(AnimationF32Target, cond=has_param2_target)
    angle_start = StructField(AnimationF32Target, cond=has_param3_target)
    angle_end = StructField(AnimationF32Target, cond=has_param4_target)
    z_size = StructField(AnimationF32Target, cond=has_param5_target)


class AnimationF32LineParamsFrame(Structure):
    length = StructField(AnimationF32Target, cond=has_param1_target)
    x_rot = StructField(AnimationF32Target, cond=has_param2_target)
    y_rot = StructField(AnimationF32Target, cond=has_param3_target)
    z_rot = StructField(AnimationF32Target, cond=has_param4_target)


class AnimationF32CubeParamsFrame(Structure):
    x_size = StructField(AnimationF32Target, cond=has_param1_target)
    y_size = StructField(AnimationF32Target, cond=has_param2_target)
    z_size = StructField(AnimationF32Target, cond=has_param3_target)
    inner_radius = StructField(AnimationF32Target, cond=has_param4_target)


class AnimationF32CylindereSphereTorusParamsFrame(Structure):
    x_size = StructField(AnimationF32Target, cond=has_param1_target)
    inner_radius = StructField(AnimationF32Target, cond=has_param2_target)
    angle_start = StructField(AnimationF32Target, cond=has_param3_target)
    angle_end = StructField(AnimationF32Target, cond=has_param4_target)
    y_size = StructField(AnimationF32Target, cond=has_param5_target)
    z_size = StructField(AnimationF32Target, cond=has_param6_target)


class AnimationF32Frame(KeyFrameBase):
    def has_random_seed(self, _) -> bool:
        return self.value_type == KeyType.Random

    def get_frame_data(self) -> Field:
        single_target_anims = [AnimTargetF32.Texture1Rotation.name, AnimTargetF32.Texture2Rotation.name,
                            AnimTargetF32.TextureIndRotation.name, AnimTargetEmitterF32.EmitterEmissionRatio.name,
                            AnimTargetEmitterF32.EmitterSpeedOrig.name, AnimTargetEmitterF32.EmitterSpeedYAxis.name,
                            AnimTargetEmitterF32.EmitterSpeedRandom.name, AnimTargetEmitterF32.EmitterSpeedNormal.name,
                            AnimTargetEmitterF32.EmitterSpeedSpecDir]

        target = get_anim_header(self).target
        if target in single_target_anims:
            return StructField(AnimationF32SingleTargetFrame, True)
        elif target != AnimTargetEmitterF32.EmitterParam.name:
            return StructField(AnimationF32VectorFrame)

        shape = get_emitter(self).emitter_flags.shape
        if shape == EmitterShape.Disc:
            return StructField(AnimationF32DiscParamsFrame)
        elif shape == EmitterShape.Line:
            return StructField(AnimationF32LineParamsFrame)
        elif shape == EmitterShape.Cube:
            return StructField(AnimationF32CubeParamsFrame)
        elif shape != EmitterShape.Point:
            return StructField(AnimationF32CylindereSphereTorusParamsFrame)
        else:
            raise ValueError('Emitter parameter animations are not supported by Point shaped emitters!')

    random_seed = u16(cond=has_random_seed)
    targets = UnionField(get_frame_data)

####################################
# Parsed Random Pool Entry Formats #
####################################

class AnimationF32RandomPoolSingleTarget(Structure):
    def has_target(self, _) -> bool:
        return check_enabled_target(self, AnimationF32VectorTargets.X)

    x = ListField(f32(), 2, cond=has_target)


class AnimationF32RandomPoolVectorTarget(Structure):
    def has_x_target(self, _) -> bool:
        return check_enabled_target(self, AnimationF32VectorTargets.X)

    def has_y_target(self, _) -> bool:
        return check_enabled_target(self, AnimationF32VectorTargets.Y)

    def has_z_target(self, _) -> bool:
        return check_enabled_target(self, AnimationF32VectorTargets.Z)

    x = ListField(f32(), 2, cond=has_x_target)
    y = ListField(f32(), 2, cond=has_y_target)
    z = ListField(f32(), 2, cond=has_z_target)


class AnimationF32RandomPoolDiscParamsTarget(Structure):
    x_size = ListField(f32(), 2, cond=has_param1_target)
    inner_radius = ListField(f32(), 2, cond=has_param2_target)
    angle_start = ListField(f32(), 2, cond=has_param3_target)
    angle_end = ListField(f32(), 2, cond=has_param4_target)
    z_size = ListField(f32(), 2, cond=has_param5_target)


class AnimationF32RandomPoolLineParamsTarget(Structure):
    length = ListField(f32(), 2, cond=has_param1_target)
    x_rot = ListField(f32(), 2, cond=has_param2_target)
    y_rot = ListField(f32(), 2, cond=has_param3_target)
    z_rot = ListField(f32(), 2, cond=has_param4_target)


class AnimationF32RandomPoolCubeParamsTarget(Structure):
    x_size = ListField(f32(), 2, cond=has_param1_target)
    y_size = ListField(f32(), 2, cond=has_param2_target)
    z_size = ListField(f32(), 2, cond=has_param3_target)
    inner_radius = ListField(f32(), 2, cond=has_param4_target)


class AnimationF32RandomPoolCylindereSphereTorusParamsTarget(Structure):
    x_size = ListField(f32(), 2, cond=has_param1_target)
    inner_radius = ListField(f32(), 2, cond=has_param2_target)
    angle_start = ListField(f32(), 2, cond=has_param3_target)
    angle_end = ListField(f32(), 2, cond=has_param4_target)
    y_size = ListField(f32(), 2, cond=has_param5_target)
    z_size = ListField(f32(), 2, cond=has_param6_target)


class AnimationF32RandomPoolEntry(Structure):
    def get_entry_data(self) -> Field:
        single_target_anims = [AnimTargetF32.Texture1Rotation.name, AnimTargetF32.Texture2Rotation.name,
                            AnimTargetF32.TextureIndRotation.name, AnimTargetEmitterF32.EmitterEmissionRatio.name,
                            AnimTargetEmitterF32.EmitterSpeedOrig.name, AnimTargetEmitterF32.EmitterSpeedYAxis.name,
                            AnimTargetEmitterF32.EmitterSpeedRandom.name, AnimTargetEmitterF32.EmitterSpeedNormal.name,
                            AnimTargetEmitterF32.EmitterSpeedSpecDir]

        target = get_anim_header(self).target
        if target in single_target_anims:
            return StructField(AnimationF32RandomPoolSingleTarget, True)
        elif target != AnimTargetEmitterF32.EmitterParam.name:
            return StructField(AnimationF32RandomPoolVectorTarget)

        shape = get_emitter(self).emitter_flags.shape
        if shape == EmitterShape.Disc:
            return StructField(AnimationF32RandomPoolDiscParamsTarget)
        elif shape == EmitterShape.Line:
            return StructField(AnimationF32RandomPoolLineParamsTarget)
        elif shape == EmitterShape.Cube:
            return StructField(AnimationF32RandomPoolCubeParamsTarget)
        elif shape != EmitterShape.Point:
            return StructField(AnimationF32RandomPoolCylindereSphereTorusParamsTarget)
        else:
            raise ValueError('Emitter parameter animations are not supported by Point shaped emitters!')

    targets = UnionField(get_entry_data)

###############
# Main Format #
###############

class AnimationF32(Structure):
    def get_key_count(self) -> int:
        return self.frame_table.entry_count

    def has_range_table(self, is_json: bool) -> bool:
        return not is_json and self.parent.range_table_size != 0

    def get_range_count(self) -> int:
        return self.range_table.entry_count

    def has_random_table(self, is_json: bool) -> bool:
        return not is_json and self.parent.random_table_size != 0

    def get_random_count(self) -> int:
        return self.random_table.entry_count

    def get_targets(self) -> IntFlag:
        if get_anim_header(self).target == AnimTargetEmitterF32.EmitterParam.name:
            return AnimationF32ParamTargets
        else:
            return AnimationF32VectorTargets

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
        targets = self.get_targets()
        emitter = get_emitter(self)
        emitter_shape = emitter.emitter_flags.shape
        param_names = list(emitter.shape_params._fields_.keys()) if emitter_shape != EmitterShape.Point else []

        # Parse each frame
        for frame in self.frames:

            # Copy the basic info
            parsed_frame = AnimationF32Frame(self)
            parsed_frame.frame = frame.frame
            parsed_frame.value_type = frame.value_type

            # Copy the random seed if necessary
            if frame.value_type == KeyType.Random:
                parsed_frame.random_seed = frame.key_data.idx

            # Create the targets field by scanning the union
            frame_data = AnimationF32Frame.targets.detect_field(parsed_frame).struct_type(parsed_frame)
            parsed_frame.targets = frame_data

            # Parse the enabled targets
            i = 0
            for target in targets:
                if check_enabled_target(frame, target):

                    # Create the target
                    target_data = AnimationF32Target(frame_data)
                    attr_name = target.name.lower()
                    if isinstance(target, AnimationF32ParamTargets):
                        attr_name = param_names[target.value.bit_length() - 1]

                    # Insert the target into the data
                    setattr(frame_data, attr_name, target_data)

                    # Get the interpolation and value/range
                    target_data.interpolation = frame.curve_types[target.value.bit_length() - 1]
                    if parsed_frame.value_type == KeyType.Fixed:
                        target_data.value = frame.key_data.values[i]
                    elif parsed_frame.value_type == KeyType.Range:
                        range_idx = frame.key_data.idx
                        range_values: AnimationF32Ranges = self.range_values[range_idx]
                        target_data.range = range_values.values[i*2 : i*2 + 2]

                    # Update the counter
                    i += 1

            # Add the parsed frame to the list
            self.key_frames.append(parsed_frame)

        # Parse the random pool entries
        for entry in self.random_values:

            # Create parsed entry
            pool_entry = AnimationF32RandomPoolEntry(self)
            entry_data = AnimationF32RandomPoolEntry.targets.detect_field(parsed_frame).struct_type(parsed_frame)
            pool_entry.targets = entry_data

            # Check the enabled targets
            i = 0
            for target in targets:
                if check_enabled_target(self, target):

                    # Get the target name
                    attr_name = target.name.lower()
                    if isinstance(target, AnimationF32ParamTargets):
                        attr_name = param_names[target.value.bit_length() - 1]

                    # Insert the range in the parsed pool entry
                    setattr(pool_entry, attr_name, entry.values[i:i+2])
                    i += 2

            # Add the new entry
            self.random_pool.append(pool_entry)

        # Let the parser do the rest
        return super().to_json()
