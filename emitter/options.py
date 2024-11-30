#!/usr/bin/env python3

# Options.py
# Emitter option definitions

from enum import auto

from common.common import CEnum
from common.field import *

class ParticleType(CEnum):
    Point = auto()
    Line = auto()
    Free = auto()
    Billboard = auto()
    Directional = auto()
    Stripe = auto()
    SmoothStripe = auto()


class Assist(CEnum):
    Normal = auto() # Render single Quad to Face surface
    Cross = auto()  # Add Quads so they are orthogonal to Normals


class BillboardAssist(CEnum):
    Normal = auto()       # Normal
    YAssist = auto()      # Y-axis billboard
    Directional = auto()  # Billboard using the movement direction as its axis
    NormalNoRoll = auto() # Normal (no roll)


class StripeAssist(CEnum):
    Normal = auto()    # Normal
    Cross = auto()     # Add a surface orthogonal to the Normal
    Billboard = auto() # Always faces the screen
    Tube = auto()      # Expression of a tube shape


class Ahead(CEnum):
    Speed = auto()          # Velocity vector direction
    EmitterCenter = auto()  # Relative position from the center of emitter
    EmitterSpecDir = auto() # Emitter specified direction
    Particle = auto()       # Difference in location from the previous particle
    User = auto()           # User specified
    NotSpecified = auto()   # Unspecified
    ParticleBoth = auto()   # Difference in position with both neighboring particles
    WorldYAxis = auto()     # Unspecified (initialized as the world Y-axis)


class BillboardAhead(CEnum):
    Speed = auto()          # Velocity vector direction
    EmitterCenter = auto()  # Relative position from the center of emitter
    EmitterSpecDir = auto() # Emitter specified direction
    Particle = auto()       # Difference in location from the previous particle
    ParticleBoth = auto()   # Difference in position with both neighboring particles


class RotateAxis(CEnum):
    XOnly = auto() # X-axis rotation only
    YOnly = auto() # Y-axis rotation only
    ZOnly = auto() # Z-axis rotation only
    XYZ = auto()   # 3-axis rotation


class Face(CEnum):
    XY = auto()
    XZ = auto()


class StripeConnect(CEnum):
    NoConnect = 0      # Does not connect
    Ring      = 1 << 0 # Both ends connected
    Emitter   = 1 << 1 # Connect between the newest particle and the emitter
    Mask      = 3


class StripeInitialPrevAxis(CEnum):
    EmitterYAxis =   0      # Y-axis of the emitter
    EmitterXAxis =   1 << 3 # X-axis of the emitter
    EmitterZAxis =   2 << 3 # Z-axis of the emitter
    EmitterXYZAxis = 3 << 3 # Direction in emitter coordinates (1, 1, 1)
    Mask           = 3 << 3


class StripeTexmapType(CEnum):
    Stretch = 0      # Stretch the texture along the stripe's entire length
    Repeat  = 1 << 6 # Repeats the texture for each segment
    Mask    = 1 << 6


class DirectionalPivot(CEnum):
    NoPivot = auto()   # No processing
    Billboard = auto() # Convert into a billboard, with the movement direction as its axis


class PointLineFreeOptions(Structure):
    expression = EnumField(Assist)
    y_direction = EnumField(Ahead)
    rotational_axis = EnumField(RotateAxis, 'B4x')


class BillboardOptions(Structure):
    expression = EnumField(BillboardAssist)
    y_direction = EnumField(BillboardAhead)
    rotational_axis = EnumField(RotateAxis, 'B4x')


class DirectionalOptions(Structure):
    expression = EnumField(Assist)
    y_direction = EnumField(Ahead)
    rotational_axis = EnumField(RotateAxis)
    speed_based_vertical = boolean()
    render_surface = EnumField(Face)
    directional_pivot = EnumField(DirectionalPivot, 'Bx')


class StripeOptions(Structure):
    expression = EnumField(StripeAssist)
    y_direction = EnumField(Ahead)
    rotational_axis = EnumField(RotateAxis)
    num_tube_vertices = u8('Bx')
    type2 = u8('Bx', skip_json=True)

    connect = EnumField(StripeConnect, skip_binary=True)
    initial_prev_axis = EnumField(StripeInitialPrevAxis, skip_binary=True)
    texmap_type = EnumField(StripeTexmapType, skip_binary=True)

    def to_json(self) -> dict:
        self.connect = StripeConnect(self.type2 & StripeConnect.Mask)
        self.initial_prev_axis = StripeInitialPrevAxis(self.type2 & StripeInitialPrevAxis.Mask)
        self.texmap_type = StripeTexmapType(self.type2 & StripeTexmapType.Mask)
        return super().to_json()

    def to_bytes(self) -> bytes:
        self.type2 = int(self.connect) | int(self.initial_prev_axis) | int(self.texmap_type)
        return super().to_bytes()


class SmoothStripeOptions(Structure):
    expression = EnumField(StripeAssist)
    y_direction = EnumField(Ahead)
    rotational_axis = EnumField(RotateAxis)
    num_tube_vertices = u8()
    num_interpolation_divisions = u8()
    type2 = u8('Bx', skip_json=True)

    connect = EnumField(StripeConnect, skip_binary=True)
    initial_prev_axis = EnumField(StripeInitialPrevAxis, skip_binary=True)
    texmap_type = EnumField(StripeTexmapType, skip_binary=True)

    def to_json(self) -> dict:
        self.connect = StripeConnect(self.type2 & StripeConnect.Mask)
        self.initial_prev_axis = StripeInitialPrevAxis(self.type2 & StripeInitialPrevAxis.Mask)
        self.texmap_type = StripeTexmapType(self.type2 & StripeTexmapType.Mask)
        return super().to_json()

    def to_bytes(self) -> bytes:
        self.type2 = int(self.connect) | int(self.initial_prev_axis) | int(self.texmap_type)
        return super().to_bytes()


def get_options(emitter: Structure) -> Field:
    match emitter.particle_type:
        case ParticleType.Billboard:
            return StructField(BillboardOptions)
        case ParticleType.Directional:
            return StructField(DirectionalOptions)
        case ParticleType.Stripe:
            return StructField(StripeOptions)
        case ParticleType.SmoothStripe:
            return StructField(SmoothStripeOptions)
        case _:
            return StructField(PointLineFreeOptions)
