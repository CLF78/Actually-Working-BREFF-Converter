#!/usr/bin/env python3

# anim_types.py
# Animation type definitions

from enum import Enum, Flag

class AnimTarget(Enum):
    # Particle U8 values
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

    # Particle F32 values
    ParticleSize = 16
    ParticleScale = 24
    Texture1Scale = 44
    Texture1Rotation = 68
    Texture1Translation = 80
    Texture2Scale = 52
    Texture2Rotation = 72
    Texture2Translation = 88
    TextureIndScale = 60
    TextureIndRotation = 76
    TextureIndTranslation = 96

    # Rotate values (uses curve type F32 if baked)
    ParticleRotation = 32

    # Texture values
    Texture1 = 104
    Texture2 = 108
    TextureInd = 112

    # Child values
    Child = 0

    # Field values
    FieldGravity = 0
    FieldSpeed = 1
    FieldMagnet = 2
    FieldNewton = 3
    FieldVortex = 4
    FieldSpin = 6
    FieldRandom = 7
    FieldTail = 8

    # PostField value
    PostFieldSize = 0
    PostFieldRotation = 12
    PostFieldTranslation = 24

    # Emitter values
    # TODO figure out what emitter field each of these affects for more accurate names
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

    @staticmethod
    def get_from_target(target: AnimTarget, baked: bool) -> 'AnimType':
        match target:

            case AnimTarget.Color1Primary | AnimTarget.Alpha1Primary | AnimTarget.Color1Secondary | \
                 AnimTarget.Alpha1Secondary | AnimTarget.Color2Primary | AnimTarget.Alpha2Primary | \
                 AnimTarget.Color2Secondary | AnimTarget.Alpha2Secondary | AnimTarget.AlphaCompareRef0 | \
                 AnimTarget.AlphaCompareRef1:
                return AnimType.ParticleU8

            case AnimTarget.ParticleSize | AnimTarget.ParticleScale | AnimTarget.Texture1Scale | \
                 AnimTarget.Texture1Rotation | AnimTarget.Texture1Translation | AnimTarget.Texture2Scale | \
                 AnimTarget.Texture2Rotation | AnimTarget.Texture2Translation | AnimTarget.TextureIndScale | \
                 AnimTarget.TextureIndRotation | AnimTarget.TextureIndTranslation:
                return AnimType.ParticleF32

            case AnimTarget.ParticleRotation:
                return AnimType.ParticleF32 if baked else AnimType.ParticleRotate

            case AnimTarget.Texture1 | AnimTarget.Texture2 | AnimTarget.TextureInd:
                return AnimType.ParticleTexture

            case AnimTarget.Child:
                return AnimType.Child

            case AnimTarget.FieldGravity | AnimTarget.FieldSpeed | AnimTarget.FieldMagnet | \
                 AnimTarget.FieldNewton | AnimTarget.FieldVortex | AnimTarget.FieldSpin | \
                 AnimTarget.FieldRandom | AnimTarget.FieldTail:
                return AnimType.Field

            case AnimTarget.PostFieldSize | AnimTarget.PostFieldRotation | AnimTarget.PostFieldTranslation:
                return AnimType.PostField

            case AnimTarget.EmitterParam | AnimTarget.EmitterScale | AnimTarget.EmitterRotation | \
                 AnimTarget.EmitterTranslation | AnimTarget.EmitterSpeedOrig | AnimTarget.EmitterSpeedYAxis | \
                 AnimTarget.EmitterSpeedRandom | AnimTarget.EmitterSpeedNormal | AnimTarget.EmitterSpeedSpecDir | \
                 AnimTarget.EmitterEmission:
                return AnimType.EmitterF32


class AnimProcessFlag(Flag):
    SyncRand      = 1 << 2
    Stop          = 1 << 3
    EmitterTiming = 1 << 4
    InfiniteLoop  = 1 << 5
    Turn          = 1 << 6
    Fitting       = 1 << 7
