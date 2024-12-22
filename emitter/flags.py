#!/usr/bin/env python3

# flags.py
# Emitter flag definitions

from enum import IntEnum, IntFlag
from common.field import *

class CommonFlag(IntFlag):
    SyncChildrenLifetime       = 1 << 0  # Child elements are also deleted when the emitter is deleted
    Invisible                  = 1 << 1  # Suppresses the rendering of the ParticleManager held by this emitter (does not propagate to child emitters)
    InfiniteLifetime           = 1 << 2  # The emitter has an infinite lifetime (maximum u32 value)
    InheritParticleScale       = 1 << 5  # Represents the Follow (particle) Scale setting
    InheritParticleRotate      = 1 << 6  # Represents the Follow (particle) Rotate setting
    InheritChildEmitterScale   = 1 << 7  # Represents the Follow (child/emitter generation) Scale setting
    InheritChildEmitterRotate  = 1 << 8  # Represents the Follow (child/emitter generation) Rotate setting
    DisableEmitterCalculations = 1 << 9  # Emitter calculations are suppressed
    InheritParticlePivot       = 1 << 10 # Sets the parent emitter to be the center of the Follow (particle) Scale and Rotate
    InheritChildPivot          = 1 << 11 # Sets the child emitter to be the center of the Follow Scale and Rotate (??)
    InheritChildParticleScale  = 1 << 12 # Represents the Follow (child/particle generation) Scale setting
    InheritChildParticleRotate = 1 << 13 # Represents the Follow (child/particle generation) Rotate setting
    RelocateComplete           = 1 << 31 # ??


class EmitterShape(IntEnum):
    Disc     = 0
    Line     = 1
    Cube     = 5
    Cylinder = 7
    Sphere   = 8
    Point    = 9
    Torus    = 10


class EmitFlag(IntFlag):
    LodEnabled    = 1 << 0  # Enables LOD
    Unk4          = 1 << 2  # Does not seem to have any effect
    BillboardY    = 1 << 7  # Enables Billboard Y
    Billboard     = 1 << 8  # Enables Billboard
    FixedInterval = 1 << 9  # Disables emitter interval randomness
    FixedPosition = 1 << 10 # Disables emitter interval position
    Instance      = 1 << 11 # ??


class TypeSpecificFlag(IntFlag):
    FlatDensity = 1 << 0 # Makes the density uniform (Disc, Cube, Cylinder, Sphere, Torus)
    LinkedSize  = 1 << 1 # Links size of Y and Z to X (Cube, Sphere) or Z to X (Disc, Cylinder, Torus)
    LineCenter  = 1 << 2 # Line only, not sure of the purpose


class DrawFlag(IntFlag):
    ZCompareEnabled             = 1 << 0  # Z-compare is enabled
    ZUpdateEnabled              = 1 << 1  # Z-update is enabled
    ZCompareBeforeTex           = 1 << 2  # Z-compare is performed before texture processing
    ClippingDisabled            = 1 << 3  # Clipping is disabled
    UseTexture1                 = 1 << 4  # Texture 1 is to be used
    UseTexture2                 = 1 << 5  # Texture 2 is to be used
    UseIndirectTexture          = 1 << 6  # The indirect texture is to be used
    IsTexture1Projection        = 1 << 7  # Texture 1 is a projection texture
    IsTexture2Projection        = 1 << 8  # Texture 2 is a projection texture
    IsIndirectTextureProjection = 1 << 9  # The indirect texture is a projection texture
    Invisible                   = 1 << 10 # Drawing is disabled
    ReverseDrawOrder            = 1 << 11 # Particles are drawn in reverse order
    FogEnabled                  = 1 << 12 # Fog settings are to be used
    XYLinkSize                  = 1 << 13 # X is to be used in place of Y which is the basic size of the particle
    XYLinkScale                 = 1 << 14 # X is to be used in place of Y which is the scale of the particle


class EmitterFlags(Structure):
    type_specific_flags = FlagEnumField(TypeSpecificFlag)
    emit_flags = FlagEnumField(EmitFlag, 'H')
    shape = EnumField(EmitterShape)

    def get_allowed_flags(self) -> TypeSpecificFlag:
        if self.shape == EmitterShape.Line:
            return TypeSpecificFlag.LineCenter
        elif self.shape != EmitterShape.Point:
            return TypeSpecificFlag.FlatDensity | TypeSpecificFlag.LinkedSize
        return TypeSpecificFlag(0)

    def to_json(self) -> dict:
        data = super().to_json()

        # Remove all flags that are not allowed
        for flag in TypeSpecificFlag:
            if flag not in self.get_allowed_flags():
                data[snake_to_camel('type_specific_flags')].pop(pascal_to_camel(flag.name))
                self.type_specific_flags &= ~flag

        # Return data
        return data

    def encode(self) -> None:
        self.type_specific_flags &= self.get_allowed_flags() # Remove all flags that are not allowed
        super().encode()
