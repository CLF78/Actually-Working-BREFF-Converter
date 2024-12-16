#!/usr/bin/env python3

# header.py
# Animation header definition

from common.field import *
from animations.common import *
from animations.flags import *
from animations.types.child import AnimationChild
from animations.types.u8 import AnimationU8
from animations.types.u8baked import AnimationU8Baked
from animations.types.f32 import AnimationF32
from animations.types.f32baked import AnimationF32Baked
from animations.types.field import AnimationField
from animations.types.rotate import AnimationRotate
from animations.types.tex import AnimationTex

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

    def get_sub_targets(self) -> Field:

        # Get the target type
        target = get_target_from_type(self.curve_type, self.kind_type)

        # For emitter parameters, use the dedicated map
        if target == AnimTargetEmitterF32.EmitterParam.name:
            shape = get_emitter(self).emitter_flags.shape
            enum_type = get_emitter_param_targets(shape)

        # Else use the generic function
        else:
            enum_type = get_sub_targets_from_type(self.curve_type, self.kind_type)

        # If only one target is available, skip the field when converting to JSON
        if enum_type is None or enum_type == AnimationSingleTarget:
            return FlagEnumField(AnimationSingleTarget, cond=skip_json)
        else:
            return FlagEnumField(enum_type)

    def get_anim_data(self) -> Field:

        # Insert necessary data in the class
        self.target = get_target_from_type(self.curve_type, self.kind_type)
        self.is_baked = self.magic == 0xAB

        # Create the data
        # TODO finish writing method
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

            # Unknown data type (yet)
            case _:
                return padding(1)

    magic = u8(cond=skip_json)
    kind_type = u8(cond=skip_json)
    curve_type = EnumField(AnimType, cond=skip_json)

    # Stupid ass workaround for Python's inability to properly handle duplicate enum values
    target = string(cond=skip_binary)
    sub_targets = UnionField(get_sub_targets)
    is_init = boolean(cond=skip_binary)
    is_baked = boolean(cond=skip_binary)

    process_flag = FlagEnumField(AnimProcessFlag)
    loop_count = u8(cond=has_loop_count)
    random_seed = u16()
    frame_count = u16('H2x', default=1, cond=has_frame_count)

    # TODO remove these from the JSON
    key_table_size = u32()
    range_table_size = u32()
    random_table_size = u32()
    name_table_size = u32()
    info_table_size = u32()

    data = UnionField(get_anim_data)

    # TODO remove this
    @classmethod
    def from_bytes(cls, data: bytes, offset: int = 0, parent: Optional[Structure] = None) -> tuple[Structure, int]:
        data, _ = super().from_bytes(data, offset, parent)
        return data, offset + data.size()

    # TODO remove this
    def size(self, start_field: Optional[Field] = None, end_field: Optional[Field] = None) -> int:
        size = super().size(start_field, end_field if end_field else AnimationHeader.info_table_size)

        if end_field is None:
            size += self.key_table_size + self.range_table_size + self.random_table_size + \
                    self.name_table_size + self.info_table_size

        return size
