#!/usr/bin/env python3

# header.py
# Animation header definition

from common.field import *
from animations.common import *
from animations.flags import *
from animations.types.child import AnimationChild
from animations.types.f32 import AnimationF32
from animations.types.f32baked import AnimationF32Baked
from animations.types.field import AnimationField
from animations.types.postfield import AnimationPostField
from animations.types.rotate import AnimationRotate
from animations.types.tex import AnimationTex
from animations.types.u8 import AnimationU8
from animations.types.u8baked import AnimationU8Baked

class AnimProcessFlag(IntFlag):
    SyncRand        = 1 << 2
    Stop            = 1 << 3 # Animation processes are stopped.
    EmitterTiming   = 1 << 4 # The animation will run during emitter time.
    LoopInfinitely  = 1 << 5 # The animation loops infinitely.
    LoopByRepeating = 1 << 6 # The animation loops by repeating (if looping is enabled).
    Fitting         = 1 << 7 # Expansion and contraction are performed according to the lifetime.


class AnimationHeader(Structure):
    def has_frame_count(self, is_json: bool) -> bool:
        return not is_json or not (self.is_baked or self.is_init)

    def has_loop_count(self, is_json: bool) -> bool:
        return not is_json or (self.process_flag & AnimProcessFlag.LoopInfinitely) == 0

    def has_sub_targets(self, is_json: bool) -> bool:
        return not is_json or get_sub_targets_from_target(self.target) != AnimationSingleTarget

    def get_sub_targets(self, is_json: bool) -> Field:

        # Get the target type
        target = self.target if is_json else get_target_from_type(self.curve_type, self.kind_type)

        # For emitter parameters, use the dedicated map
        if target == AnimTargetEmitterF32.EmitterParam.name:
            shape = get_emitter(self).emitter_flags.shape
            enum_type = get_emitter_param_targets(shape)

        # Else use the generic function
        elif is_json:
            enum_type = get_sub_targets_from_target(self.target)
        else:
            enum_type = get_sub_targets_from_type(self.curve_type, self.kind_type)

        # If only one target is available, skip the field when converting to JSON
        if enum_type is None or enum_type == AnimationSingleTarget:
            return FlagEnumField(AnimationSingleTarget, default=AnimationSingleTarget.T, cond=skip_json)
        else:
            return FlagEnumField(enum_type)

    def get_anim_data(self, is_json: bool) -> Field:

        # Insert necessary data in the class
        if is_json:
            self.magic = 0xAB if self.is_baked else 0xAC
            self.kind_type = get_kind_value_from_target(self.target).value
            self.curve_type = get_type_from_target(self.target)
        else:
            self.target = get_target_from_type(self.curve_type, self.kind_type)
            self.is_baked = self.magic == 0xAB

        # Create the data
        match self.curve_type:
            case AnimType.ParticleU8:
                return StructField(AnimationU8 if not self.is_baked else AnimationU8Baked, True)

            case AnimType.Child:
                return StructField(AnimationChild, True)

            case AnimType.ParticleF32 | AnimType.EmitterF32:
                return StructField(AnimationF32 if not self.is_baked else AnimationF32Baked, True)

            case AnimType.ParticleRotate:
                return StructField(AnimationRotate, True)

            case AnimType.ParticleTexture:
                return StructField(AnimationTex, True)

            case AnimType.Field:
                return StructField(AnimationField, True)

            case AnimType.PostField:
                return StructField(AnimationPostField, True)

    magic = u8(cond=skip_json)
    kind_type = u8(cond=skip_json)
    curve_type = EnumField(AnimType, cond=skip_json)

    # Stupid ass workaround for Python's inability to properly handle duplicate enum values
    target = string(cond=skip_binary)
    sub_targets = UnionField(get_sub_targets, cond=has_sub_targets)
    is_init = boolean(cond=skip_binary)
    is_baked = boolean(cond=skip_binary)

    process_flag = FlagEnumField(AnimProcessFlag)
    loop_count = u8(default=0, cond=has_loop_count)
    random_seed = u16()
    frame_count = u16('H2x', default=1, cond=has_frame_count)

    key_table_size = u32(default=0, cond=skip_json)
    range_table_size = u32(default=0, cond=skip_json)
    random_table_size = u32(default=0, cond=skip_json)
    name_table_size = u32(default=0, cond=skip_json)
    info_table_size = u32(default=0, cond=skip_json)

    data = UnionField(get_anim_data)
