#!/usr/bin/env python3

# anim_types.py
# Animation type definitions

from enum import Enum, Flag

class AnimProcessFlag(Flag):
    SyncRand        = 1 << 2
    Stop            = 1 << 3 # Animation processes are stopped.
    EmitterTiming   = 1 << 4 # The animation will run during emitter time.
    LoopInfinitely  = 1 << 5 # The animation loops infinitely.
    LoopByRepeating = 1 << 6 # The animation loops by repeating (if looping is enabled).
    Fitting         = 1 << 7 # Expansion and contraction are performed according to the lifetime.


class AnimTargetU8(Enum):
    Color1Primary = 0
    Alpha1Primary = 3
    Color1Secondary = 4
    Alpha1Secondary  = 7
    Color2Primary  = 8
    Alpha2Primary  = 11
    Color2Secondary  = 12
    Alpha2Secondary  = 15
    AlphaCompareRef0 = 119
    AlphaCompareRef1 = 120


class AnimTargetF32(Enum):
    ParticleSize = 16
    ParticleScale = 24
    ParticleRotation = 32
    Texture1Scale = 44
    Texture1Rotation = 68
    Texture1Translation = 80
    Texture2Scale = 52
    Texture2Rotation = 72
    Texture2Translation = 88
    TextureIndScale = 60
    TextureIndRotation = 76
    TextureIndTranslation = 96


class AnimTargetRotate(Enum):
    ParticleRotation = 32


class AnimTargetTexture(Enum):
    Texture1 = 104
    Texture2 = 108
    TextureInd = 112


class AnimTargetChild(Enum):
    Child = 0


class AnimTargetField(Enum):
    FieldGravity = 0
    FieldSpeed = 1
    FieldMagnet = 2
    FieldNewton = 3
    FieldVortex = 4
    FieldSpin = 6
    FieldRandom = 7
    FieldTail = 8


class AnimTargetPostField(Enum):
    PostFieldSize = 0
    PostFieldRotation = 12
    PostFieldTranslation = 24


# TODO figure out what emitter field each of these affects for more accurate names
class AnimTargetEmitterF32(Enum):
    EmitterParam = 44
    EmitterScale = 124
    EmitterRotation = 136
    EmitterTranslation = 112
    EmitterSpeedOrig = 72
    EmitterSpeedYAxis = 76
    EmitterSpeedRandom = 80
    EmitterSpeedNormal = 84
    EmitterSpeedSpecDir = 92
    EmitterEmission = 8


class AnimType(Enum):
    ParticleU8 = 0
    PostField = 2 # v11 only?
    ParticleF32 = 3
    ParticleTexture = 4
    Child = 5
    ParticleRotate = 6 # For baked rotations, ParticleF32 is used instead
    Field = 7
    EmitterF32 = 11


TargetTypeMap = {
    AnimType.ParticleU8: {
        AnimTargetU8.Color1Primary, AnimTargetU8.Alpha1Primary, AnimTargetU8.Color1Secondary,
        AnimTargetU8.Alpha1Secondary, AnimTargetU8.Color2Primary, AnimTargetU8.Alpha2Primary,
        AnimTargetU8.Color2Secondary, AnimTargetU8.Alpha2Secondary, AnimTargetU8.AlphaCompareRef0,
        AnimTargetU8.AlphaCompareRef1
    },

    AnimType.ParticleF32: {
        AnimTargetF32.ParticleSize, AnimTargetF32.ParticleScale, AnimTargetF32.Texture1Scale,
        AnimTargetF32.Texture1Rotation, AnimTargetF32.Texture1Translation, AnimTargetF32.Texture2Scale,
        AnimTargetF32.Texture2Rotation, AnimTargetF32.Texture2Translation, AnimTargetF32.TextureIndScale,
        AnimTargetF32.TextureIndRotation, AnimTargetF32.TextureIndTranslation, AnimTargetF32.ParticleRotation
    },

    AnimType.ParticleRotate: {AnimTargetRotate.ParticleRotation},

    AnimType.ParticleTexture: {
        AnimTargetTexture.Texture1, AnimTargetTexture.Texture2, AnimTargetTexture.TextureInd
    },

    AnimType.Child: {AnimTargetChild.Child},

    AnimType.Field: {
        AnimTargetField.FieldGravity, AnimTargetField.FieldSpeed, AnimTargetField.FieldMagnet,
        AnimTargetField.FieldNewton, AnimTargetField.FieldVortex, AnimTargetField.FieldSpin,
        AnimTargetField.FieldRandom, AnimTargetField.FieldTail
    },

    AnimType.PostField: {
        AnimTargetPostField.PostFieldSize, AnimTargetPostField.PostFieldRotation,
        AnimTargetPostField.PostFieldTranslation
    },

    AnimType.EmitterF32: {
        AnimTargetEmitterF32.EmitterParam, AnimTargetEmitterF32.EmitterScale,
        AnimTargetEmitterF32.EmitterRotation, AnimTargetEmitterF32.EmitterTranslation,
        AnimTargetEmitterF32.EmitterSpeedOrig, AnimTargetEmitterF32.EmitterSpeedYAxis,
        AnimTargetEmitterF32.EmitterSpeedRandom, AnimTargetEmitterF32.EmitterSpeedNormal,
        AnimTargetEmitterF32.EmitterSpeedSpecDir, AnimTargetEmitterF32.EmitterEmission
    }
}


def get_type_from_target(target: Enum, baked: bool) -> AnimType:
    for anim_type, targets in TargetTypeMap.items():
        if target in targets:
            return AnimType.ParticleF32 if (anim_type == AnimType.ParticleRotate and baked) else anim_type
    raise ValueError(f'Unknown target: {target}')


def get_target_from_type(type: AnimType, kind_value: int) -> Enum:
    for target in TargetTypeMap[type]:
        if target.value == kind_value:
            return target
    raise ValueError(f'Unknown target {kind_value} for animation type {type}')


# Stupid ass workaround for Python's inability to properly handle duplicate enum values
def get_target_from_string(target: str) -> Enum:
    for targets in TargetTypeMap.values():
        for value in targets:
            if value.name == target:
                return value
    raise ValueError(f'Unknown target: {target}')
