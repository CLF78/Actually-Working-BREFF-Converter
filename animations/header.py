#!/usr/bin/env python3

# header.py
# Animation header definition

from common.field import *
from animations.flags import *
from animations.types.u8 import AnimationU8

def get_anim_data(header: 'AnimationHeader') -> Field:

    # Get necessary data
    header.is_baked = header.magic == 0xAB
    header.target = get_target_from_type(header.curve_type, header.kind_type)

    # Create the data
    # TODO write method
    match header.target:
        case AnimTargetU8.Color1Primary.name | AnimTargetU8.Alpha1Primary.name | \
             AnimTargetU8.Color1Secondary.name | AnimTargetU8.Alpha1Secondary.name | \
             AnimTargetU8.Color2Primary.name | AnimTargetU8.Alpha2Primary.name | \
             AnimTargetU8.Color2Secondary.name | AnimTargetU8.Alpha2Secondary.name | \
             AnimTargetU8.AlphaCompareRef0.name | AnimTargetU8.AlphaCompareRef1.name:
            return StructField(AnimationU8, True) if not header.is_baked else padding(1)

        # Unknown data type (yet)
        case _:
            return padding(1)


class AnimationHeader(Structure):

    # Stupid ass workaround for Python's inability to properly handle duplicate enum values
    target = string(skip_binary=True)
    is_init = boolean(skip_binary=True)
    is_baked = boolean(skip_binary=True)

    magic = u8(skip_json=True)
    kind_type = u8(skip_json=True)
    curve_type = EnumField(AnimType, skip_json=True)
    kind_enable = u8(skip_json=True)

    process_flag = FlagEnumField(AnimProcessFlag)
    loop_count = u8()
    random_seed = u16()
    frame_count = u16('H2x', default=1, cond=lambda x: not x.is_init)

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

    def get_param_count(self):
        return bin(self.kind_enable).count('1')
