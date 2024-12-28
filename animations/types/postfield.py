#!/usr/bin/env python3

# postfield.py
# PostField animation definitions

from enum import IntFlag, auto
from common.common import CEnum
from common.field import *
from common.nw4r import VEC3
from animations.common import *
from animations.tables import *
from animations.types.f32 import AnimationF32
from animations.types.child import AnimationChildParam


class SpeedControlType(CEnum):
    NoControl = auto()
    Limit = auto()
    Kill = auto()


class CollisionShape(CEnum):
    Plane = auto()
    Rectangle = auto()
    Circle = auto()
    Cube = auto()
    Sphere = auto()
    Cylinder = auto()


class CollisionShapeOptionsPlane(CEnum):
    XZ = auto()
    XY = auto()
    YZ = auto()


class CollisionShapeOptionsSphere(CEnum):
    Whole = auto()
    Top = auto()
    Bottom = auto()


class CollisionType(CEnum):
    Border = auto()
    Inside = auto()
    Outside = auto()


class CollisionOptions(IntFlag):
    EmitterOriented     = 1 << 0
    Bounce              = 1 << 1
    ControlSpeed        = 1 << 3
    CreateChildParticle = 1 << 4
    CreateChildEmitter  = 1 << 5
    Kill                = 1 << 6


class WrapOptions(IntFlag):
    WrapEnabled = auto()
    WrapCenterEmitter = auto()


class AnimationPostFieldChildDummy(Structure):
    padd = padding(12)


class AnimationPostFieldInfo(Structure):
    def get_shape_options(self, _) -> Field:
        match self.collision_shape:
            case CollisionShape.Plane | CollisionShape.Rectangle | CollisionShape.Circle:
                return EnumField(CollisionShapeOptionsPlane)
            case CollisionShape.Sphere:
                return EnumField(CollisionShapeOptionsSphere)
            case _:
                return u8(default=0, cond=skip_json)

    def get_child_info(self, is_json: bool) -> Field:
        if is_json or get_anim_header(self).name_table_size != 0:
            return StructField(AnimationChildParam)
        else:
            return StructField(AnimationPostFieldChildDummy)

    scale = StructField(VEC3)
    rotation = StructField(VEC3)
    translation = StructField(VEC3)
    reference_speed = f32()
    speed_control_type = EnumField(SpeedControlType)
    collision_shape = EnumField(CollisionShape)
    collision_shape_options = UnionField(get_shape_options)
    collision_type = EnumField(CollisionType)
    collision_options = FlagEnumField(CollisionOptions, 'H')
    start_frame = u16()
    speed_factor = StructField(VEC3)
    child_params = UnionField(get_child_info)
    wrap_options = FlagEnumField(WrapOptions, 'B3x')
    wrap_scale = StructField(VEC3)
    wrap_rotation = StructField(VEC3)
    wrap_translation = StructField(VEC3)


class AnimationPostField(Structure):
    def has_frames(self, _) -> bool:
        return get_anim_header(self).sub_targets.value != 0

    def has_name_table(self, is_json: bool) -> bool:
        return not is_json and get_anim_header(self).name_table_size != 0

    frames = StructField(AnimationF32, unroll=True, cond=has_frames)
    name_table = StructField(NameTable, cond=has_name_table, alignment=4)
    info = StructField(AnimationPostFieldInfo)

    def encode(self) -> None:

        # Create the name table if necessary
        child_params: AnimationChildParam = self.info.child_params
        if child_params.name:
            self.name_table = NameTable(self)

        # Calculate info table size
        anim_header = get_anim_header(self)
        anim_header.info_table_size = self.info.size()

        # Do encoding
        super().encode()

        # Calculate name table size
        if self.name_table:
            anim_header.name_table_size = self.size(AnimationPostField.name_table,
                                                    AnimationPostField.name_table, True)
