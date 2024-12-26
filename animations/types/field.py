#!/usr/bin/env python3

# field.py
# Field animation definitions

from enum import IntFlag, auto
from common.common import CEnum
from common.field import *
from common.nw4r import VEC3
from animations.common import *
from animations.tables import *
from animations.types.f32 import AnimationF32
from animations.types.f32baked import AnimationF32Baked


class Space(CEnum):
    Global = auto()
    Emitter = auto()
    ParticleManager = auto()
    GlobalWithScale = auto()


class AddTarget(CEnum):
    Velocity = auto()
    Speed = auto()


class OptionRandom(IntFlag):
    RandomSaveVelocity = 1 << 0
    RandomAllDirection = 1 << 1
    RandomEnableX      = 1 << 2
    RandomEnableY      = 1 << 3
    RandomEnableZ      = 1 << 4


class InfoFieldSpeed(Structure):
    speed = f32()


class InfoFieldGravity(Structure):
    power = f32()
    rotation = StructField(VEC3)


class InfoFieldRandom(Structure):
    power = f32()
    diffusion = f32()
    interval = u16('H2x')


class InfoFieldSpin(Structure):
    speed = f32()
    rotation = StructField(VEC3)


class InfoFieldMagnet(Structure):
    power = f32()
    translation = StructField(VEC3)


class InfoFieldNewton(Structure):
    power = f32()
    ref_distance = f32()
    translation = StructField(VEC3)


class InfoFieldVortex(Structure):
    inner_speed = f32()
    outer_speed = f32()
    distance = f32()
    translation = StructField(VEC3)


class InfoFieldTail(Structure):
    power = f32()


class AnimationFieldInfo(Structure):
    def get_field_info(self, _) -> Field:
        match get_anim_header(self).target:
            case AnimTargetField.FieldGravity.name:
                return StructField(InfoFieldGravity, unroll=True)
            case AnimTargetField.FieldMagnet.name:
                return StructField(InfoFieldMagnet, unroll=True)
            case AnimTargetField.FieldNewton.name:
                return StructField(InfoFieldNewton, unroll=True)
            case AnimTargetField.FieldRandom.name:
                return StructField(InfoFieldRandom, unroll=True)
            case AnimTargetField.FieldSpeed.name:
                return StructField(InfoFieldSpeed, unroll=True)
            case AnimTargetField.FieldSpin.name:
                return StructField(InfoFieldSpin, unroll=True)
            case AnimTargetField.FieldTail.name:
                return StructField(InfoFieldTail, unroll=True)
            case AnimTargetField.FieldVortex.name:
                return StructField(InfoFieldVortex, unroll=True)

    space = EnumField(Space)
    addTarget = EnumField(AddTarget, 'Bx')
    option = FlagEnumField(OptionRandom)
    data = UnionField(get_field_info)


class AnimationField(Structure):
    def has_frames(self, _) -> bool:
        return get_anim_header(self).sub_targets.value != 0

    def get_frame_format(self, _) -> Field:
        if get_anim_header(self).is_baked:
            return StructField(AnimationF32Baked, unroll=True)
        else:
            return StructField(AnimationF32, unroll=True)

    frames = UnionField(get_frame_format, cond=has_frames)
    info = StructField(AnimationFieldInfo)

    def encode(self) -> None:
        super().encode()
        get_anim_header(self).info_table_size = self.info.size()
