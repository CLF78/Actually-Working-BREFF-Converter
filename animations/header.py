#!/usr/bin/env python3

# header.py
# Animation header definition

from common.field import *
from animations.flags import *
from animations.types.child import AnimationChild
from animations.types.u8 import AnimationU8
from animations.types.u8baked import AnimationU8Baked
from animations.types.f32 import AnimationF32
from animations.types.f32baked import AnimationF32Baked

class AnimationHeader(Structure):
    def has_frame_count(self, is_json: bool) -> bool:
        return not is_json or not (self.is_baked or self.is_init)

    def has_loop_count(self, is_json: bool) -> bool:
        return not is_json or (self.process_flag & AnimProcessFlag.LoopInfinitely) == 0

    def get_param_count(self):
        return bin(self.kind_enable).count('1')

    def get_anim_data(self) -> Field:

        # Get necessary data
        self.target = get_target_from_type(self.curve_type, self.kind_type)
        self.is_baked = self.magic == 0xAB

        # Create the data
        # TODO finish writing method
        match self.curve_type:
            case AnimType.ParticleU8:
                return StructField(AnimationU8 if not self.is_baked else AnimationU8Baked, True)

            case AnimType.Child:
                return StructField(AnimationChild, True)

            case AnimType.ParticleF32:
                return StructField(AnimationF32 if not self.is_baked else AnimationF32Baked, True)

            # Unknown data type (yet)
            case _:
                return padding(1)

    # Stupid ass workaround for Python's inability to properly handle duplicate enum values
    target = string(cond=skip_binary)
    is_init = boolean(cond=skip_binary)
    is_baked = boolean(cond=skip_binary)

    magic = u8(cond=skip_json)
    kind_type = u8(cond=skip_json)
    curve_type = EnumField(AnimType, cond=skip_json)
    kind_enable = u8(cond=skip_json)

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

    # TODO remove this garbage
    @classmethod
    def from_bytes(cls, data: bytes, offset: int = 0, parent: Optional[Structure] = None) -> tuple[Structure, int]:
        data, _ = super().from_bytes(data, offset, parent)
        return data, offset + data.size()

    def to_bytes(self) -> bytes:

        # Set values
        self.magic = 0xAB if self.is_baked else 0xAC
        target = get_target_from_string(self.target)
        self.kind_type = target.value
        self.curve_type = get_type_from_target(target, self.is_baked)
        return super().to_bytes()

    def size(self, start_field: Optional[Field] = None, end_field: Optional[Field] = None) -> int:
        size = super().size(start_field, end_field if end_field else AnimationHeader.info_table_size)

        if end_field is None:
            size += self.key_table_size + self.range_table_size + self.random_table_size + \
                    self.name_table_size + self.info_table_size

        return size
