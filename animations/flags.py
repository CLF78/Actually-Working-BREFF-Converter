#!/usr/bin/env python3

# targets.py
# Animation target definitions

from enum import IntEnum, IntFlag, auto
from emitter.flags import EmitterShape

########################
# Main Animation Types #
########################

class AnimType(IntEnum):
    ParticleU8 = 0
    PostField = 2 # v11 only?
    ParticleF32 = 3
    ParticleTexture = 4
    Child = 5
    ParticleRotate = 6 # For baked rotations, ParticleF32 is used instead
    Field = 7
    EmitterF32 = 11

###########
# Targets #
###########

class AnimTargetU8(IntEnum):
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


class AnimTargetF32(IntEnum):
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


class AnimTargetRotate(IntEnum):
    ParticleRotate = 32


class AnimTargetTexture(IntEnum):
    Texture1 = 104
    Texture2 = 108
    TextureInd = 112


class AnimTargetChild(IntEnum):
    Child = 0


class AnimTargetField(IntEnum):
    FieldGravity = 0
    FieldSpeed = 1
    FieldMagnet = 2
    FieldNewton = 3
    FieldVortex = 4
    FieldSpin = 6
    FieldRandom = 7
    FieldTail = 8


class AnimTargetPostField(IntEnum):
    PostFieldSize = 0
    PostFieldRotation = 12
    PostFieldTranslation = 24


# These are offsets in the EmitterParameter structure, and not the raw emitter data
class AnimTargetEmitterF32(IntEnum):
    EmitterEmissionRatio = 8 # 1 param
    EmitterParam = 44        # 1 to 6 params, depending on shape
    EmitterSpeedOrig = 72    # 1 param - vel power radiation dir
    EmitterSpeedYAxis = 76   # 1 param - vel power y axis
    EmitterSpeedRandom = 80  # 1 param - vel power random dir
    EmitterSpeedNormal = 84  # 1 param - vel power normal dir
    EmitterSpeedSpecDir = 92 # 5 params - vel power spec dir, vel diffusion spec dir, vel spec dir
    EmitterTranslation = 112 # 3 params
    EmitterScale = 124       # 3 params
    EmitterRotation = 136    # 3 params

###############
# Sub-targets #
###############

class AnimationColorTargets(IntFlag):
    R = auto()
    G = auto()
    B = auto()


class AnimationSingleTarget(IntFlag):
    T = auto()


class AnimationVec2Targets(IntFlag):
    X = auto()
    Y = auto()


class AnimationVec3Targets(IntFlag):
    X = auto()
    Y = auto()
    Z = auto()


class AnimationDiscParamTargets(IntFlag):
    XSize = auto()
    InnerRadius = auto()
    AngleStart = auto()
    AngleEnd = auto()
    ZSize = auto()


class AnimationLineParamTargets(IntFlag):
    Length = auto()
    XRot = auto()
    YRot = auto()
    ZRot = auto()


class AnimationCubeParamTargets(IntFlag):
    XSize = auto()
    YSize = auto()
    ZSize = auto()
    InnerRadius = auto()


class AnimationCylinderSphereTorusParamTargets(IntFlag):
    XSize = auto()
    InnerRadius = auto()
    AngleStart = auto()
    AngleEnd = auto()
    YSize = auto()
    ZSize = auto()


class AnimationEmitterSpeedSpecDirTargets(IntFlag):
    PowerSpecDir = auto()
    DiffusionSpecDir = auto()
    VelSpecDirX = auto()
    VelSpecDirY = auto()
    VelSpecDirZ = auto()


class AnimationFieldSpeedTargets(IntFlag):
    Speed = auto()


class AnimationFieldTailTargets(IntFlag):
    Power = auto()


class AnimationFieldGravityTargets(IntFlag):
    Power = auto()
    XRot = auto()
    YRot = auto()
    ZRot = auto()


class AnimationFieldRandomTargets(IntFlag):
    Power = auto()
    Diffusion = auto()


class AnimationFieldSpinTargets(IntFlag):
    Speed = auto()
    XRot = auto()
    YRot = auto()
    ZRot = auto()


class AnimationFieldMagnetTargets(IntFlag):
    Power = auto()
    XTrans = auto()
    YTrans = auto()
    ZTrans = auto()


class AnimationFieldNewtonTargets(IntFlag):
    Power = auto()
    RefDistance = auto()
    XTrans = auto()
    YTrans = auto()
    ZTrans = auto()


class AnimationFieldVortexTargets(IntFlag):
    InnerSpeed = auto()
    OuterSpeed = auto()
    Distance = auto()
    XTrans = auto()
    YTrans = auto()
    ZTrans = auto()


TargetTypeMap = {
    AnimType.ParticleU8: {
        AnimTargetU8.Color1Primary: AnimationColorTargets,
        AnimTargetU8.Alpha1Primary: AnimationSingleTarget,
        AnimTargetU8.Color1Secondary: AnimationColorTargets,
        AnimTargetU8.Alpha1Secondary: AnimationSingleTarget,
        AnimTargetU8.Color2Primary: AnimationColorTargets,
        AnimTargetU8.Alpha2Primary: AnimationSingleTarget,
        AnimTargetU8.Color2Secondary: AnimationColorTargets,
        AnimTargetU8.Alpha2Secondary: AnimationSingleTarget,
        AnimTargetU8.AlphaCompareRef0: AnimationSingleTarget,
        AnimTargetU8.AlphaCompareRef1: AnimationSingleTarget,
    },

    AnimType.ParticleF32: {
        AnimTargetF32.ParticleSize: AnimationVec2Targets,
        AnimTargetF32.ParticleScale: AnimationVec2Targets,
        AnimTargetF32.Texture1Scale: AnimationVec2Targets,
        AnimTargetF32.Texture1Rotation: AnimationSingleTarget,
        AnimTargetF32.Texture1Translation: AnimationVec2Targets,
        AnimTargetF32.Texture2Scale: AnimationVec2Targets,
        AnimTargetF32.Texture2Rotation: AnimationSingleTarget,
        AnimTargetF32.Texture2Translation: AnimationVec2Targets,
        AnimTargetF32.TextureIndScale: AnimationVec2Targets,
        AnimTargetF32.TextureIndRotation: AnimationSingleTarget,
        AnimTargetF32.TextureIndTranslation: AnimationVec2Targets,
        AnimTargetF32.ParticleRotation: AnimationVec3Targets,
    },

    AnimType.ParticleRotate: {
        AnimTargetRotate.ParticleRotate: AnimationVec3Targets,
    },

    AnimType.ParticleTexture: {
        AnimTargetTexture.Texture1: AnimationSingleTarget,
        AnimTargetTexture.Texture2: AnimationSingleTarget,
        AnimTargetTexture.TextureInd: AnimationSingleTarget,
    },

    AnimType.Child: {
        AnimTargetChild.Child: AnimationSingleTarget,
    },

    AnimType.Field: {
        AnimTargetField.FieldGravity: AnimationFieldGravityTargets,
        AnimTargetField.FieldSpeed: AnimationFieldSpeedTargets,
        AnimTargetField.FieldMagnet: AnimationFieldMagnetTargets,
        AnimTargetField.FieldNewton: AnimationFieldNewtonTargets,
        AnimTargetField.FieldVortex: AnimationFieldVortexTargets,
        AnimTargetField.FieldSpin: AnimationFieldSpinTargets,
        AnimTargetField.FieldRandom: AnimationFieldRandomTargets,
        AnimTargetField.FieldTail: AnimationFieldTailTargets,
    },

    AnimType.PostField: {
        AnimTargetPostField.PostFieldSize: AnimationVec3Targets,
        AnimTargetPostField.PostFieldRotation: AnimationVec3Targets,
        AnimTargetPostField.PostFieldTranslation: AnimationVec3Targets,
    },

    AnimType.EmitterF32: {
        AnimTargetEmitterF32.EmitterParam: None,
        AnimTargetEmitterF32.EmitterScale: AnimationVec3Targets,
        AnimTargetEmitterF32.EmitterRotation: AnimationVec3Targets,
        AnimTargetEmitterF32.EmitterTranslation: AnimationVec3Targets,
        AnimTargetEmitterF32.EmitterSpeedOrig: AnimationSingleTarget,
        AnimTargetEmitterF32.EmitterSpeedYAxis: AnimationSingleTarget,
        AnimTargetEmitterF32.EmitterSpeedRandom: AnimationSingleTarget,
        AnimTargetEmitterF32.EmitterSpeedNormal: AnimationSingleTarget,
        AnimTargetEmitterF32.EmitterSpeedSpecDir: AnimationEmitterSpeedSpecDirTargets,
        AnimTargetEmitterF32.EmitterEmissionRatio: AnimationSingleTarget,
    }
}

EmitterParamMap = {
    EmitterShape.Disc: AnimationDiscParamTargets,
    EmitterShape.Line: AnimationLineParamTargets,
    EmitterShape.Cube: AnimationCubeParamTargets,
    EmitterShape.Cylinder: AnimationCylinderSphereTorusParamTargets,
    EmitterShape.Sphere: AnimationCylinderSphereTorusParamTargets,
    EmitterShape.Point: None,
    EmitterShape.Torus: AnimationCylinderSphereTorusParamTargets,
}

def get_target_from_type(type: AnimType, kind_value: int) -> str:
    for target in TargetTypeMap[type]:
        if target == kind_value:
            return target.name
    raise ValueError(f'Unknown target {kind_value} for animation type {type}')

def get_sub_targets_from_type(type: AnimType, kind_value: int) -> IntFlag:
    for target, sub_targets in TargetTypeMap[type].items():
        if target == kind_value:
            return sub_targets
    raise ValueError(f'Unknown target {kind_value} for animation type {type}')

def get_emitter_param_targets(shape: EmitterShape):
    return EmitterParamMap[shape]
